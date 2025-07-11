import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # <-- импортируем декоратор
from django.http import JsonResponse
import requests

from .forms import DocumentUploadForm
from .models import Document, UserToDocument, Price, Cart


def index(request):
    documents = Document.objects.all()
    return render(request, 'core/index.html', {'documents': documents})


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.cleaned_data['file']

            save_path = os.path.join(settings.MEDIA_ROOT, upload_file.name)
            with open(save_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

            size_kb = upload_file.size / 1024

            document = Document.objects.create(
                file_path=os.path.join('media', upload_file.name),
                size=size_kb
            )

            UserToDocument.objects.create(
                username=request.user.username,
                document=document
            )

            return redirect('index')
    else:
        form = DocumentUploadForm()

    return render(request, 'core/upload.html', {'form': form})


@login_required
def order_analysis(request):
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        document = Document.objects.get(id=doc_id)

        file_ext = document.file_path.split('.')[-1].lower()
        price_obj = Price.objects.filter(file_type=file_ext).first()
        if not price_obj:
            return render(request, 'core/order.html', {
                'documents': Document.objects.all(),
                'error': f'Нет цены для типа файла: .{file_ext}'
            })

        total_price = document.size * price_obj.price

        Cart.objects.create(
            user=request.user,
            document=document,
            order_price=total_price,
            payment=False
        )

        return redirect('index')

    documents = Document.objects.all()
    return render(request, 'core/order.html', {'documents': documents})


@login_required
def cart_view(request):
    user_orders = Cart.objects.filter(user=request.user)
    return render(request, 'core/cart.html', {'orders': user_orders})


@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Cart, id=order_id, user=request.user)
    if request.method == 'POST':
        order.payment = True
        order.save()
        # Здесь можно добавить логику отправки в FastAPI
        return redirect('cart')
    return render(request, 'core/pay_order.html', {'order': order})


@login_required
def upload_to_fastapi(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    file_path = os.path.join(settings.BASE_DIR, document.file_path)

    if not os.path.exists(file_path):
        return JsonResponse({'error': 'Файл не найден на сервере'}, status=404)

    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        response = requests.post(
            'http://fastapi_service:8001/upload_doc',  # <-- ИСПРАВЛЕНО: обращаемся по имени контейнера
            files={'file': (os.path.basename(file_path), file_data, 'application/octet-stream')}
        )
    except Exception as e:
        return JsonResponse({'error': f'Ошибка при отправке файла: {e}'}, status=500)

    if response.status_code == 200:
        return redirect('index')
    else:
        return JsonResponse({
            'error': f'Ошибка при загрузке во FastAPI: {response.text}'
        }, status=response.status_code)


@login_required
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    full_path = os.path.join(settings.BASE_DIR, document.file_path)

    if os.path.isfile(full_path):
        os.remove(full_path)

    document.delete()
    return redirect('index')


@login_required
@csrf_exempt  # <-- ИСПРАВЛЕНИЕ: отключаем CSRF, т.к. запрос идёт из внешнего клиента
def analyse_document_view(request):
    result = None
    error = None

    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        if not doc_id or not doc_id.isdigit():
            error = "Введите корректный ID документа"
        else:
            try:
                response = requests.post(
                    f'http://fastapi_service:8001/doc_analyse?doc_id={int(doc_id)}'
                )
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('message', 'Анализ запущен')
                else:
                    error = f"Ошибка от FastAPI: {response.json().get('detail', 'неизвестная ошибка')}"
            except Exception as e:
                error = f"Ошибка подключения к FastAPI: {e}"

    return render(request, 'core/analyse_document.html', {
        'result': result,
        'error': error,
    })


@login_required
@csrf_exempt  # <-- ИСПРАВЛЕНИЕ: отключаем CSRF для GET с внешнего источника, если вызывается POST, тоже можно поставить
def get_text_view(request):
    result = None
    error = None

    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        if not doc_id or not doc_id.isdigit():
            error = "Введите корректный ID документа"
        else:
            try:
                response = requests.get('http://fastapi_service:8001/get_text', params={"doc_id": int(doc_id)})
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('text', '')
                else:
                    error = f"Ошибка от FastAPI: {response.json().get('detail', 'неизвестная ошибка')}"
            except Exception as e:
                error = f"Ошибка подключения к FastAPI: {e}"

    return render(request, 'core/get_text.html', {
        'result': result,
        'error': error,
    })





