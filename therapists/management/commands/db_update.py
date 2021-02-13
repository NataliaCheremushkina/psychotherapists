import requests
from django.utils import timezone
from django.core.management.base import BaseCommand
from therapists.models import Therapist, DBUpdate


class Command(BaseCommand):
    help = 'Get data from Airtable and update PostgreSQL data'

    def add_arguments(self, parser):
        parser.add_argument('--key', dest='key', type=str)
        parser.add_argument('--base_id', dest='base_id', type=str)
        parser.add_argument('--base_name', dest='base_name', type=str)

    def parse_airtable_data(self, airtable_data):
        return {(rec['id'],
                 rec['fields']['Имя'],
                 rec['fields']['Фотография'][0]['url'],
                 ', '.join(rec['fields']['Методы']))
                for rec in airtable_data['records']}

    def get_airtable(self, **options):
        headers = {'Authorization': f'Bearer {options["key"]}'}
        url = f'https://api.airtable.com/v0/{options["base_id"]}/{options["base_name"]}'
        return requests.get(url, headers=headers)

    def process_data(self, airtable_data, postgres_data):
        diff_data = list(airtable_data - postgres_data)
        air_id = [rec[0] for rec in diff_data]
        for rec in (postgres_data - airtable_data):
            if rec[0] not in air_id:
                diff_data.append(rec)

        return diff_data

    def handle(self, *args, **options):
        airtable_resp = self.get_airtable(**options)
        if airtable_resp.status_code != 200:
            raise ConnectionError(f'Bad options, status: {airtable_resp.status_code}')

        airtable_data = self.parse_airtable_data(airtable_resp.json())
        DBUpdate.objects.create(update_datetime=timezone.now(), data=airtable_data)

        postgres_data = set(Therapist.objects.all().values_list())

        diff_data = self.process_data(airtable_data, postgres_data)

        airtable_id = [rec[0] for rec in airtable_data]
        postgres_id = [rec[0] for rec in postgres_data]

        for rec in diff_data:
            rec_id = rec[0]

            if rec_id in airtable_id and rec_id in postgres_id:
                update_fields = {}
                postgres_rec = [rec for rec in postgres_data if rec[0] == rec_id][0]

                for fld, air_fld, post_fld in zip(('name', 'photo', 'methods'),
                                                  rec[1:],
                                                  postgres_rec[1:]):
                    if air_fld != post_fld:
                        update_fields.update({fld: air_fld})

                Therapist.objects.filter(id=rec_id).update(**update_fields)

            elif rec_id in airtable_id and rec_id not in postgres_id:
                Therapist.objects.create(id=rec[0], name=rec[1], photo=rec[2], methods=rec[3])

            elif rec_id not in airtable_id and rec_id in postgres_id:
                Therapist.objects.get(id=rec_id).delete()

        self.stdout.write(f'{len(diff_data)} records in PostgreSQL was updated')
