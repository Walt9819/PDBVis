import requests
import os

def downloadModelFromDB(ID, outPath, baseURL='https://files.rcsb.org/download/'):
    #print('Requesting {my_id} file. Please wait.\n'.format(my_id=ID))
    reqURL = os.path.join(baseURL, ID.lower() + '.pdb')
    response = requests.get(reqURL)
    if not response.ok:
        #print('ID {my_id} file not founded. Try with other ID.\n'.format(my_id=ID))
        return False
    #print('ID:{my_id} file was downloaded. Writing file.\n'.format(my_id=ID))
    with open(os.path.join(outPath, ID + ".pdb"), "w+") as f:
        f.write(response.text)
    return True
