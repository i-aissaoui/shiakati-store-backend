SELECT v.id, v.product_id, v.size, v.color, v.barcode, p.name FROM variants v JOIN products p ON v.product_id = p.id LIMIT 5;
