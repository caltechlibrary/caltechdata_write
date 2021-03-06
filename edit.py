import argparse, os, json
from caltechdata_api import caltechdata_edit

parser = argparse.ArgumentParser(description=\
        "Write files and a DataCite 4 standard json record\
        to CaltechDATA repository")
parser.add_argument('json_file', nargs=1, help=\
            'file name for json DataCite metadata file')
parser.add_argument('-ids', nargs='*', help='CaltechDATA IDs')
parser.add_argument('-fnames', nargs='*', help='New Files')
parser.add_argument('-schema', default="40", help="Metadata Schema")
args = parser.parse_args()

#Get access token from TIND set as environment variable with source token.bash
token = os.environ['TINDTOK']

metaf = open(args.json_file[0], 'r')
metadata = json.load(metaf)

production = True

response = caltechdata_edit(token, args.ids, metadata, args.fnames, {'pdf'}, production, args.schema)
print(response)
