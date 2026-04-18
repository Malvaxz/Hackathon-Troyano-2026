from data_sources.mongo_reader import get_latest_bed_record

data = get_latest_bed_record()
print(data)