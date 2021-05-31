from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
import os
import io

def getModel(request, modelID=None):
    if request.method == "GET":
        print(modelID)
        buffer = io.open('models/fbx/NaCl.fbx', 'rb')
        buffer.seek(0)
        #return FileResponse(buffer, as_attachment=True, filename='hello.fbx')
        return JsonResponse({'Message': f'Valid ID {modelID}'}, status=201)
    else:
        return JsonResponse({'Error': 'Invalid method'}, status=404)
