# look at all JAR files in a directory and print out information
# to help us understand the different versions of the game

import hashlib, os, sys, zipfile

def file_hash(path):
    h = hashlib.sha256()

    with open(path, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)

    return h.hexdigest()

def read_manifest(z):
    manifest = {}

    with z.open('META-INF/MANIFEST.MF', 'r') as manifest_file:
        for line in manifest_file:
            line = line.decode().strip()
            if not line: continue
            [key, value] = line.split(':')
            manifest[key.strip()] = value.strip()

    return manifest

all_bins = []

for name in os.listdir(sys.argv[1]):
    if not name.endswith('.jar'): continue
    #print(name)
    path = os.path.join(sys.argv[1], name)
    size = os.stat(path).st_size
    hash = file_hash(path)

    with zipfile.ZipFile(path, mode='r') as z:
        manifest = read_manifest(z)

        contents_size = 0
        h = hashlib.sha256()

        for info in z.infolist():
            contents_size += info.file_size

            with z.open(info.filename, 'r') as f:
                for b in iter(lambda : f.read(128*1024), b''):
                    h.update(b)

        contents_hash = h.hexdigest()

    if hash == '03f5b6f9e8e16617db0ffdaa7db0c3abd8c0d50ddf31fe935f78143cf55bf697':
        note = 'GoF 2 v1.0.3 RU (Fan Patch?)'
    elif hash == '235c6960c6cc714a538eca61b92b453473eb7dd8e8344e1c5b23fed5d6c2fc0a':
        note = 'GoF 1.1.2 RU'
        tested = 'minexew_w595, some graphics stretched'
    elif hash == '271b69a582e60b4c1bb09a53bb0756e6842fdd17ca3808538336b19881fc7e56':
        note = 'GoF v1.0.3 DE (Retail?)'
        tested = 'minexew_w595, some graphics stretched'
    elif hash == '29d07ade596b5bc27e79e8c8604d01e283df205595dbb7b6a142ffcbf4229e83':
        note = 'GoF v1.4.8 CZ Fan Translation'
        tested = 'minexew_w595, runs well'
    elif hash == '3eaf078773b7886c5cc1abd2159f93e06af87cdd96258ed29afcae71bc13f11a':
        note = 'GoF v1.2 CZ Fan Translation'
        tested = 'minexew_w595, some graphics stretched'
    elif hash == '4c039e7584dd99a2f91f22b6812e53d93ba03cde601052dd1249769772559bc6':
        note = 'GoF v1.2 or newer, EN, with adware'
        tested = 'minexew_w595, some graphics stretched'
    elif hash == '667f81069891da5bda4929c8a068945bc4f9c099341e11eb57f570d8c6eaa3ca':
        note = 'GoF 2 v1.0.3 RU (Fan Patch?)'
    elif hash == '7b9dd10e64267cd758a9e8ffd52c488c86822d4a236aa32a825365a43f8732ce':
        note = 'GoF v1.0.3 CZ Fan Translation'
    elif hash == '9d8e7d5fcc795c92be34c09ebe10480827d055248d114f975a91000bb0901382':
        note = 'GoF 2 v1.0.3 SK Fan Translation'
    elif hash == 'a5ac630affe0ef222a37abcb67980421dabced79c60d618d2c578a3574cbc08f':
        note = 'Deep v1.0.3 EN (Retail?)'
        tested = 'minexew_w595'
    elif hash == 'aab2276684609839c541b818b290fb4e8087405407ce273dd9256e2dc5386791':
        note = 'GoF 2 v1.0.3 EN (Retail?)'
    elif hash == 'c2b47c4a6eebe2fd36d40cc4300103c0012c62b60748a185a8e4e6eddd0b4d41':
        note = 'Deep v1.0.8 EN (Hacked?)'
        tested = 'minexew_w595, laggy & graphical errors'
    elif hash == 'ca467a324e310bf44ca5733c457ceadcb1ef33d73449bd586c199919172f2157':
        note = 'GoF v1.2.9 EN (hacked version)'
        tested = 'minexew_w595, runs well'
    elif hash == 'd8013fad92f69418ee73ffd01e99bcf44ef108bad7c830367bd35095badcca8e':
        note = 'Deep v1.0.2 EN (Retail?)'
        tested = 'minexew_w595'
    elif hash == 'ddd6503d2a047cf5fc02987e446ef3e64ec7a04d8ad908850c873cb322ebebca':
        note = 'GoF v1.2.9 EN (M3G API version)'
        tested = 'minexew_w595, hangs pre-menu'
    elif hash == 'ea9dce67fad4c0f139ef7d6b616593981216942d592988a47d5e918d938fd0d5':
        note = 'GoF v1.1.2 EN (176x208 version?)'
        tested = 'minexew_w595, some graphics stretched'
    elif hash == 'f40d40f3efd8d2f34e12752a550770429770a7fa651b9e39adcbeece28ad17c9':
        note = 'GoF v1.2.9 EN (M3G API version)'
        tested = ['minexew_w595, hangs pre-menu', 'minexew_kemulator, runs']
    elif hash == 'f8944d71919230dc9e9c4343b8a7fdab7706665e578ed572f4c0ec65315c54bf':
        note = 'GoF 2 v1.0.3 RU (Fan Patch?)'
    elif hash == 'ff74b33a1eabe5bf37528ee633328cde08ceac00a810f8f41ff3e6faa6ff5c09':
        node = 'GoF v1.1.2 EN (176x208 version?)'
        tested = 'minexew_w595, some graphics stretched'
    else:
        note = None

    all_bins.append(dict(path=path, name=name, size=size, hash=hash,
            contents_size=contents_size, contents_hash=contents_hash,
            manifest=manifest, note=note))

all_bins = sorted(all_bins, key=lambda d: d['contents_size'], reverse=True)

print('Name,Size,SHA-256,Contents_Size,Contents_Hash,MIDlet-Name,MIDlet-Version,MIDlet-Vendor,Note')

for d in all_bins:
    print('%s,%d,%s,%d,%s,%s,%s,%s,"%s"' % (
        d['name'],
        d['size'],
        d['hash'],
        d['contents_size'],
        d['contents_hash'],
        d['manifest']['MIDlet-Name'],
        d['manifest']['MIDlet-Version'],
        d['manifest']['MIDlet-Vendor'],
        d['note'] or '',
        ))
