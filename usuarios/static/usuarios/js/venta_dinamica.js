/* ============================================
   PowerMedical - Venta Dinámica
   Tabla dinámica de detalles de venta
   ============================================ */

(function () {
    'use strict';

    let rowIndex = 0;
    let productosData = [];

    function init() {
        const container = document.getElementById('detalles-container');
        const btnAdd = document.getElementById('btn-add-row');
        const productosScript = document.getElementById('productos-data');

        if (!container || !btnAdd) return;

        if (productosScript) {
            try {
                productosData = JSON.parse(productosScript.textContent);
            } catch (e) {
                productosData = [];
            }
        }

        btnAdd.addEventListener('click', addRow);

        if (container.children.length === 0) {
            addRow();
        }

        recalculate();
    }

    function addRow() {
        const container = document.getElementById('detalles-container');
        if (!container) return;

        const tr = document.createElement('tr');
        tr.setAttribute('data-row-index', rowIndex);

        let optionsHtml = '<option value="">-- Seleccionar --</option>';
        productosData.forEach(function (p) {
            optionsHtml += '<option value="' + p.id + '" data-precio="' + p.precio_venta + '">' +
                p.codigo + ' - ' + p.nombre + '</option>';
        });

        tr.innerHTML =
            '<td>' +
            '   <select name="det_producto_' + rowIndex + '" class="form-select form-select-sm" required>' +
            '       ' + optionsHtml +
            '   </select>' +
            '</td>' +
            '<td>' +
            '   <input type="number" name="det_cantidad_' + rowIndex + '" class="form-control form-control-sm" min="1" value="1" required>' +
            '</td>' +
            '<td>' +
            '   <input type="number" name="det_precio_' + rowIndex + '" class="form-control form-control-sm" min="0" step="0.01" value="0.00" required>' +
            '</td>' +
            '<td class="subtotal-cell text-end" style="white-space:nowrap">$0.00</td>' +
            '<td class="text-center">' +
            '   <button type="button" class="btn-remove-row" title="Eliminar fila"><i class="bi bi-trash"></i></button>' +
            '</td>';

        container.appendChild(tr);

        var select = tr.querySelector('select');
        var cantidad = tr.querySelector('input[name^="det_cantidad"]');
        var precio = tr.querySelector('input[name^="det_precio"]');
        var btnRemove = tr.querySelector('.btn-remove-row');

        select.addEventListener('change', function () {
            var opt = select.options[select.selectedIndex];
            var precioVal = opt.getAttribute('data-precio');
            if (precioVal) {
                precio.value = parseFloat(precioVal).toFixed(2);
            }
            recalculate();
        });

        cantidad.addEventListener('input', recalculate);
        precio.addEventListener('input', recalculate);

        btnRemove.addEventListener('click', function () {
            tr.remove();
            recalculate();
        });

        rowIndex++;
    }

    function recalculate() {
        var container = document.getElementById('detalles-container');
        var totalEl = document.getElementById('total-venta');
        if (!container || !totalEl) return;

        var total = 0;

        var rows = container.querySelectorAll('tr');
        rows.forEach(function (row) {
            var cantidad = parseFloat(row.querySelector('input[name^="det_cantidad"]')?.value) || 0;
            var precio = parseFloat(row.querySelector('input[name^="det_precio"]')?.value) || 0;
            var subtotal = cantidad * precio;

            var subtotalCell = row.querySelector('.subtotal-cell');
            if (subtotalCell) {
                subtotalCell.textContent = '$' + subtotal.toFixed(2);
            }

            total += subtotal;
        });

        totalEl.textContent = '$' + total.toFixed(2);
    }

    document.addEventListener('DOMContentLoaded', init);
})();
