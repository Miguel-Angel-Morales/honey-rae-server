"""View module for handling requests for service_ticket data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer


class TicketView(ViewSet):
    """Honey Rae API service_tickets view"""

    def destroy(self, request, pk=None):
        """Handle DELETE requests for single service_ticket

        Returns:
            Response -- None with 204 status code
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)


    def list(self, request):
        """Handle GET requests to get all service_tickets

        Returns:
            Response -- JSON serialized list of service_tickets
        """
        service_tickets = []

        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)

                if request.query_params['status'] == "all":
                    pass

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


    def retrieve(self, request, pk=None):
        """Handle GET requests for single service_ticket

        Returns:
            Response -- JSON serialized service_ticket record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(
            service_ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        #"Handle Put request for single customer"

        #Returns:
        #Response -- No response body. Just 204 status code.

        #Select the targeted Ticket using PK
        ticket = ServiceTicket.objects.get(pk=pk)
        #Get the employee id from the client request
        employee_id = request.data['employee']
        #Select the employee from the database using that id
        assigned_employee = Employee.objects.get(pk=employee_id)
        #Assign the Employee instance to the employee property to the ticket
        ticket.employee = assigned_employee
        #Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)



class TicketEmployeeSerializer(serializers.ModelSerializer):#For customers to see the Full_name property
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketCustomerSerializer(serializers.ModelSerializer): #For employees to see the Full_name property
    class Meta:
        model = Customer
        fields = ('id', 'user', 'address', 'full_name')
        
class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for service_ticket"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description',
                  'emergency', 'date_completed')
        depth = 1
