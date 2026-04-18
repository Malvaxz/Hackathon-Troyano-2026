from data_sources.mongo_reader import get_latest_bed_record

latest = get_latest_bed_record()
print("ULTIMO REGISTRO:")
print(latest)