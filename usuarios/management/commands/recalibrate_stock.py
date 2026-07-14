from django.core.management.base import BaseCommand
from django.db.models import Sum
from usuarios.models import Producto, Lote


class Command(BaseCommand):
    help = 'Recalcula el stock de todos los productos desde sus lotes activos.'

    def handle(self, *args, **options):
        productos = Producto.objects.all()
        corregidos = 0

        for producto in productos:
            stock_real = Lote.objects.filter(
                detalle_compra__producto=producto,
                estado='ACTIVO',
            ).aggregate(total=Sum('cantidad_recibida'))['total'] or 0

            if producto.stock != stock_real:
                self.stdout.write(
                    f'  {producto.codigo}: {producto.stock} → {stock_real}'
                )
                producto.stock = stock_real
                producto.save(update_fields=['stock'])
                corregidos += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. {corregidos} producto(s) corregido(s) de {productos.count()} total.'
        ))
