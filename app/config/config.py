import yaml

with open('/app/config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

db = config['database']

pg_conf = db['postgresql']
pg_host = pg_conf['host']
pg_port = pg_conf['port']
pg_database = pg_conf['database']
pg_user = pg_conf['user']
pg_password = pg_conf['password']
pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}/{pg_database}"

mongo_conf = db['mongo']
mongo_host = mongo_conf['host']
mongo_port = mongo_conf['port']
mongo_database = mongo_conf['database']
mongo_user = mongo_conf['user']
mongo_password = mongo_conf['password']
# 'mongodb://myuser:mypassword@localhost:27017/mydatabase'
mongo_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"


file_dir = config['file_dir']
excel_file_dir = file_dir['excel']
excel_complete_file_dir = file_dir['excel_complete']