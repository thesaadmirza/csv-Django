from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
from rest_framework.generics import CreateAPIView
from .serializer import InvoiceFile_Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv, io
from django.shortcuts import render, HttpResponseRedirect, reverse
import codecs
from .models import Invoice
from django.contrib import messages
import logging
from .forms import InvoiceForm
from django.db.models import Sum


def uploadcsv(request):
    data = {}
    if "GET" == request.method:
        return render(request, "base.html", data)
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return HttpResponseRedirect(reverse("csv_app:upload_csv"))
        # if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("csv_app:upload_csv"))

        file_data = csv_file.read().decode("utf-8")

        io_string = io.StringIO(file_data) #Convert Data to ISO string to be readable by Csv library

        # loop over the lines and save them in db. If error , store as string and then display
        i = 0
        for fields in csv.reader(io_string, skipinitialspace=True): # this is the code which read the data and don't skip it from delimeter ","
            # only allow after header
            if (i): #only allow after header values
                if (len(fields) > 19):
                    data_dict = {}
                    data_dict["contactName"] = fields[0]
                    data_dict["invoiceNumber"] = fields[10]
                    data_dict["invoiceDate"] = datetime.strptime(fields[12], '%d/%m/%Y')# converting date string to datetime object
                    data_dict["dueDate"] = datetime.strptime(fields[13], '%d/%m/%Y') # converting date string to datetime object
                    data_dict["description"] = fields[16]
                    data_dict["quantity"] = fields[17]
                    data_dict["unitAmount"] = fields[18]
                    try:
                        #add Invoice Directly to model
                        test = Invoice.objects.create(contactName=fields[0], invoiceNumber=fields[10],
                                                      invoiceDate=datetime.strptime(fields[12], '%d/%m/%Y'),
                                                      dueDate=datetime.strptime(fields[12], '%d/%m/%Y'),
                                                      description=fields[16], quantity=fields[17],
                                                      unitAmount=fields[18]) #adding inovice from model
                    except Exception as e:
                        print(e)
                    try:
                        form = InvoiceForm()
                        if form.is_valid():
                            form.save()
                        else:
                            logging.getLogger("error_logger").error(form.errors.as_json())
                    except Exception as e:
                        logging.getLogger("error_logger").error(form.errors.as_json())
                        pass
            i = i + 1

        #just for demo , delete after learning
        firstRow = Invoice.objects.first()
        print(firstRow)
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. " + repr(e))
        messages.error(request, "Unable to upload file. " + repr(e))

    return HttpResponseRedirect(reverse("csv-home"))


class InvoiceUploadAPIView(CreateAPIView):
    serializer_class = InvoiceFile_Serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        file_data = file.read().decode("utf-8")

        io_string = io.StringIO(file_data)

        # loop over the lines and save them in db. If error , store as string and then display
        i = 0
        for fields in csv.reader(io_string, skipinitialspace=True):
            # only allow after header
            if (i):
                if (len(fields) > 19):
                    data_dict = {}
                    data_dict["contactName"] = fields[0]
                    data_dict["invoiceNumber"] = fields[10]
                    data_dict["invoiceDate"] = datetime.strptime(fields[12], '%d/%m/%Y')
                    data_dict["dueDate"] = datetime.strptime(fields[13], '%d/%m/%Y')
                    # date dict just for demonstration
                    data_dict["description"] = fields[16]
                    data_dict["quantity"] = fields[17]
                    data_dict["unitAmount"] = fields[18]
                    try:
                        # add Invoice Directly to model
                        test = Invoice.objects.create(contactName=fields[0], invoiceNumber=fields[10],
                                                      invoiceDate=datetime.strptime(fields[12], '%d/%m/%Y'),
                                                      dueDate=datetime.strptime(fields[12], '%d/%m/%Y'),
                                                      description=fields[16], quantity=fields[17],
                                                      unitAmount=fields[18])
                        print(test)
                    except Exception as e:
                        print(e)
                    try:
                        form = InvoiceForm()
                        if form.is_valid():
                            form.save()
                        else:
                            logging.getLogger("error_logger").error(form.errors.as_json())
                    except Exception as e:
                        logging.getLogger("error_logger").error(form.errors.as_json())
                        pass
            i = i + 1

        # just for demo , delete after learning
        firstRow = Invoice.objects.first()
        print(firstRow)

        return Response(status=status.HTTP_204_NO_CONTENT)
