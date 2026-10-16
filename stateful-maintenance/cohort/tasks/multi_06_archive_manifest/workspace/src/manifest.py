import hashlib
def generate(files,output_archive):
    return {'manifest':[{'path':p,'sha256':hashlib.sha256(files[p].encode('utf-8')).hexdigest()} for p in sorted(files) if p != output_archive]}
