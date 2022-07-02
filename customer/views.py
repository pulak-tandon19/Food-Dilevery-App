import json
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from .models import MenuItem, OrderModel, Category

# Create your views here.

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')

class Order(View):
    def get(self, request, *args, **kwargs):
        #getting every item from each category
        appetizers= MenuItem.objects.filter(category__name__contains= 'Appetizer')
        entres= MenuItem.objects.filter(category__name__contains= 'Entre')
        drinks= MenuItem.objects.filter(category__name__contains= 'Drink')
        desserts= MenuItem.objects.filter(category__name__contains= 'Dessert')

        context = {
            'appetizers' : appetizers,
            'entres' : entres,
            'drinks' : drinks,
            'desserts' : desserts,
        }

        return render(request, 'customer/order.html', context)

    def post(self, request, *argts, **kwargs):

        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin_code = request.POST.get('pin')


        order_items = {
            'items' : []
        }

        items= request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk__contains= int(item))
            item_data= {
                'id' : menu_item.pk,
                'name' : menu_item.name,
                'price' : menu_item.price,
            }

            order_items['items'].append(item_data)

            price = 0 
            item_ids = []

        for item in order_items['items']:
            price+= item['price']
            item_ids.append(item['id'])

        order= OrderModel.objects.create(
            price=price,
            name= name,
            email = email,
            street= street,
            city = city,
            state = state,
            pin_code = pin_code,
        )
        order.items.add(*item_ids)

        context= {
                'items' : order_items['items'],
                'price' : price
            }

        # Sending Mail

        body = ('Your order has been placed. Your food is being prepared and will be delivered soon!\n')
        # 'Thank You again for your order! ')
        for item in order.items.all():
            body+=(f'${item.name}:- ${item.price} \n')
        body+=(f'Total:- ${order.price}')

        send_mail(
            'Thank You For Your Order!',
            body,
            'pulaktandon2000@gmail.com',
            [email],
            fail_silently = False
        )

        return redirect('order-confirmation', pk=order.pk)



class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)
        
        context={
                'pk' : order.pk,
                'items': order.items,
                'price': order.price,
            }

        return render(request, 'customer/order_confirmation.html', context)

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)

        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()
        
        return redirect('payment-confirmation', pk)

class OrderPayConfirmation(View):
    def get(self, request, pk, *args, **kwargs): 
        order = OrderModel.objects.get(pk=pk)
        body = (f'Your payment is completed.\n Show this email to delivery boy.\n Your order:-\n')
        # '{for item in order.items.all()} ${item.name} ${item.price}')
        for item in order.items.all():
            body+=(f'${item.name}:- ${item.price} \n')
        body+=(f'Total:- ${order.price}')
        send_mail(
            'Payment Confirmed!',
            body,
            'fooddelivery1219@gmail.com',
            [order.email],
            fail_silently = False
        )

        return render(request, 'customer/order_pay_confirmation.html')

class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()
        context = {
             'menu_items' : menu_items,
         }

        return render(request, 'customer/menu.html', context)

class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")
        menu_items = MenuItem.objects.filter(
            Q(name__icontains= query) |
            Q(price__icontains= query) |
            Q(description__icontains = query)
        )

        context={
            'menu_items' : menu_items
        }

        return render(request, 'customer/menu.html', context)
