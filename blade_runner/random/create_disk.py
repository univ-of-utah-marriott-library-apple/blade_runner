import subprocess as sp

vol_name = 'test_disk'
create_dmg = [
    'hdiutil',
    'create',
    '-size',
    '1g',
    '-fs',
    'HFS+J',
    '-volname',
    vol_name,
    '/tmp/' + vol_name
]
try:
    sp.check_output(create_dmg)
except:
    print('The file ' + vol_name + '.dmg' + 'already exists. Please delete it and try again.')