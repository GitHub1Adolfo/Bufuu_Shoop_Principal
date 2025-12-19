import qrcode
from io import BytesIO
import base64

def generar_qr_orden(request, orden_id, tipo='cliente'):
    """
    Genera un código QR para la orden
    
    Args:
        request: Request object de Django
        orden_id: ID de la orden
        tipo: 'cliente' o 'admin'
    
    Returns:
        String base64 de la imagen QR
    """
    # Determinar URL según tipo
    if tipo == 'admin':
        # URL para que admin edite la orden (usando 'gestion' en lugar de 'admin')
        url = request.build_absolute_uri(f'/gestion/orden/{orden_id}/editar/')
    else:
        # URL para que cliente vea su orden
        url = request.build_absolute_uri(f'/orden/{orden_id}/ver/')
    
    # Crear QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Generar imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f'data:image/png;base64,{img_str}'