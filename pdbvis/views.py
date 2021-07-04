from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
import os
import io

from .ReadPDB import PDBConverter
from .GetPDB import downloadModelFromDB

os.chdir('PDBVis/')

def modelAvailable(modelID, modelsPath="models/"):
    """
    Return if model with `modelID` is available as `fbx` or `pdb`.
    """
    print(os.listdir())
    for type in ["fbx", "pdb"]:
        files = os.listdir(os.path.join(modelsPath, type))
        for fl in files:
            fSplit = fl.split('.')
            if modelID == fSplit[0] and fSplit[-1] == type:
                return type
    return None


def getModel(request, modelID=None):
    if request.method == "GET":
        if len(modelID) != 4:
            return JsonResponse({'Error': 'Invalid model ID, must be 4 characters long.'}, status=404)

        # get if model is available as fbx, pdb or None
        availableType = modelAvailable(modelID)

        # if not available, download from DB
        if not availableType:
            if not downloadModelFromDB(modelID, 'models/pdb'):
                return JsonResponse({"Error": f"Molecule with ID {modelID} not found . Please check RCSB database for available models in: https://www.rcsb.org/"}, status=401)
            availableType = 'pdb'
        if availableType == "pdb":
            # convert from PDB into FBX
            PDBConverter(input=os.path.join('models', 'pdb', f'{modelID}.pdb', output=os.path.join('models', 'fbx', f'{modelID}.fbx')))

        buffer = io.open(os.path.join("models", "fbx", f'{modelID}.fbx'), 'rb')
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'{modelID}.fbx')
        #return JsonResponse({'Message': f'Valid ID {modelID}'}, status=201)
    else:
        return JsonResponse({'Error': 'Invalid method'}, status=404)
