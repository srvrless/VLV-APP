
-- ==== collection ==== 

CREATE OR REPLACE FUNCTION get_collection_by_id(collection_id BIGINT) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, description TEXT, "position" INT, is_hidden BOOLEAN, is_smart BOOLEAN)
AS $$
    SELECT id, parent_id, title, description, "position", is_hidden, is_smart 
    FROM collection
    WHERE id = collection_id AND NOT db_hidden;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_collection_by_title(collection_title VARCHAR) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, description TEXT, "position" INT, is_hidden BOOLEAN, is_smart BOOLEAN)
AS $$
    SELECT id, parent_id, title, description, "position", is_hidden, is_smart 
    FROM collection
    WHERE title = collection_title AND NOT db_hidden;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_collections(excluded_titles VARCHAR[]) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, description TEXT, "position" INT, is_hidden BOOLEAN, is_smart BOOLEAN)
AS $$
    SELECT id, parent_id, title, description, "position", is_hidden, is_smart
    FROM collection
    WHERE 
        NOT title = ANY(excluded_titles)
        AND NOT db_hidden;
$$ LANGUAGE SQL;


-- ==== category ====

CREATE OR REPLACE FUNCTION get_category_by_id(category_id BIGINT) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, "position" INT)
AS $$
    SELECT id, parent_id, title, "position" 
    FROM category
    WHERE id = category_id AND NOT db_hidden;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_category_by_title(category_title VARCHAR) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, "position" INT)
AS $$
    SELECT id, parent_id, title, "position" 
    FROM category
    WHERE title = category_title AND NOT db_hidden;
$$ LANGUAGE SQL;
 
CREATE OR REPLACE FUNCTION get_categories(excluded_titles VARCHAR[]) RETURNS
TABLE (id BIGINT, parent_id BIGINT, title VARCHAR, "position" INT)
AS $$
    SELECT id, parent_id, title, "position" 
    FROM category
    WHERE 
        NOT title = ANY(excluded_titles)
        AND NOT db_hidden;
$$ LANGUAGE SQL;


-- ==== product ====

CREATE OR REPLACE FUNCTION get_product_by_id(arg_product_id BIGINT) RETURNS
TABLE 
    (id BIGINT,
    category_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_hidden BOOLEAN,
    available BOOLEAN,
    archived BOOLEAN,
    canonical_url_collection_id BIGINT,
    price DECIMAL(20, 2),
    old_price DECIMAL(20, 2),
    unit VARCHAR,
    ignore_discounts BOOLEAN,
    title VARCHAR,
    description TEXT,
    currency_code VARCHAR,
    collection_ids BIGINT[],
    collection_names VARCHAR[],
    image_positions INT[],
    image_urls VARCHAR[],
    property_names VARCHAR[],
    property_values VARCHAR[]
    )
AS $$
    SELECT 
        id, category_id, created_at, updated_at, is_hidden, available, archived, canonical_url_collection_id, 
        (SELECT MIN(price) FROM variant v WHERE v.product_id = product.id),
        (SELECT MIN(old_price) FROM variant v WHERE v.product_id = product.id),
        unit, ignore_discounts, title, description, currency_code,
        ARRAY(SELECT c.id FROM collection2product c2p JOIN collection c ON c2p.collection_id = c.id AND c2p.product_id = arg_product_id WHERE NOT c.db_hidden),
        ARRAY(SELECT c.title FROM collection2product c2p JOIN collection c ON c2p.collection_id = c.id AND c2p.product_id = arg_product_id WHERE NOT c.db_hidden),
        ARRAY(SELECT "position" FROM image i WHERE product_id = arg_product_id AND NOT i.db_hidden),
        ARRAY(SELECT original_url FROM image i WHERE product_id = arg_product_id AND NOT i.db_hidden),
        ARRAY(SELECT p.title FROM product2property p2p JOIN property p ON p2p.property_id = p.id AND p2p.product_id = arg_product_id WHERE NOT p.db_hidden),
        ARRAY(SELECT p2p."value" FROM product2property p2p JOIN property p ON p2p.property_id = p.id AND p2p.product_id = arg_product_id WHERE NOT p.db_hidden)
    FROM product
    WHERE id = arg_product_id AND NOT db_hidden;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_products(min_price BIGINT, max_price BIGINT, arg_collection_ids BIGINT[], arg_category_ids BIGINT[], arg_options VARCHAR[]) RETURNS
TABLE 
    (id BIGINT,
    category_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_hidden BOOLEAN,
    available BOOLEAN,
    archived BOOLEAN,
    canonical_url_collection_id BIGINT,
    price DECIMAL(20, 2),
    old_price DECIMAL(20, 2),
    unit VARCHAR,
    ignore_discounts BOOLEAN,
    title VARCHAR,
    description TEXT,
    currency_code VARCHAR,
    collection_ids BIGINT[],
    collection_names VARCHAR[],
    image_positions INT[],
    image_urls VARCHAR[],
    property_names VARCHAR[],
    property_values VARCHAR[]
    )
AS $$
    SELECT 
        id, category_id, created_at, updated_at, is_hidden, available, archived, canonical_url_collection_id, 
        price, old_price, unit, ignore_discounts, title, description, currency_code, collection_ids, collection_names, 
        image_positions, image_urls, property_names, property_values
    FROM search_product
    WHERE
        (arg_collection_ids <@ collection_ids) AND
        (category_id = ANY(arg_category_ids) OR array_length(arg_category_ids, 1) IS NULL) AND
        (arg_options <@ search_option_and_properties) AND 
        (min_price <= price OR min_price IS NULL) AND  
        (price <= max_price OR max_price IS NULL);
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION product_get_variants(arg_product_id BIGINT) RETURNS
TABLE 
    (id BIGINT,
    title VARCHAR,
    product_id BIGINT,
    sku VARCHAR,
    available BOOLEAN,
    image_url VARCHAR,
    weight REAL,
    quantity INT,
    quantities_at_warehouses INT[],
    price DECIMAL(20, 2),
    old_price DECIMAL(20, 2),
    option_names VARCHAR[],
    option_values VARCHAR[],
    option_image_urls VARCHAR[]
    )
AS $$
    SELECT 
        id, title, product_id, sku, available, 
        (SELECT original_url FROM image WHERE id = image_id), 
        weight, quantity, quantities_at_warehouses, 
        price, old_price,
        ARRAY(SELECT o_n.title FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id),
        ARRAY(SELECT ov."value" FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id),
        ARRAY(SELECT ov.image_url FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id)
    FROM 
        variant v
    WHERE v.product_id = arg_product_id AND NOT v.db_hidden;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION product_get_variants_by_ids(product_ids BIGINT[]) RETURNS
TABLE 
    (id BIGINT,
    title VARCHAR,
    product_id BIGINT,
    sku VARCHAR,
    available BOOLEAN,
    image_url VARCHAR,
    weight REAL,
    quantity INT,
    quantities_at_warehouses INT[],
    price DECIMAL(20, 2),
    old_price DECIMAL(20, 2),
    option_names VARCHAR[],
    option_values VARCHAR[],
    option_image_urls VARCHAR[]
    )
AS $$
    SELECT 
        id, title, product_id, sku, available, 
        (SELECT original_url FROM image WHERE id = image_id), 
        weight, quantity, quantities_at_warehouses, 
        price, old_price,
        ARRAY(SELECT o_n.title FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id),
        ARRAY(SELECT ov."value" FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id),
        ARRAY(SELECT ov.image_url FROM
            variant2option_value v2ov JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
            JOIN option_name o_n ON ov.option_name_id = o_n.id)
    FROM 
        variant v
    WHERE v.product_id = ANY(product_ids) AND NOT v.db_hidden;
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION get_filter_info_by_product_ids(product_ids BIGINT[]) RETURNS
TABLE 
    (name VARCHAR,
    "values" VARCHAR[])
AS $$
    SELECT property.title, ARRAY(
        SELECT DISTINCT p2p."value"
        FROM property p JOIN product2property p2p ON p.id = p2p.property_id AND p2p.product_id = ANY (product_ids) AND p.id = sub_query.property_id
        AND NOT p.db_hidden
        )
    FROM 
        (SELECT DISTINCT p2p.property_id FROM product2property p2p WHERE p2p.product_id = ANY (product_ids) AND NOT p2p.db_hidden) AS sub_query
        JOIN property ON sub_query.property_id = property.id
    UNION
    SELECT opn.title, ARRAY(
        SELECT DISTINCT ov."value"  
        FROM 
            variant2option_value v2ov JOIN variant v ON v2ov.variant_id = v.id AND v.product_id = ANY (product_ids)
            JOIN option_value ov ON v2ov.option_value_id = ov.id AND ov.option_name_id = sub_query.option_name_id
    )
    FROM
        (SELECT DISTINCT ov.option_name_id
        FROM 
            variant2option_value v2ov JOIN variant v ON v2ov.variant_id = v.id AND v.product_id = ANY (product_ids)
            JOIN option_value ov ON v2ov.option_value_id = ov.id) AS sub_query
        JOIN option_name opn ON opn.id = sub_query.option_name_id
    UNION
    SELECT 'collection_ids', ARRAY(
        SELECT DISTINCT collection_id::VARCHAR FROM
            product p JOIN collection2product c2p ON p.id = c2p.product_id AND p.id = ANY(product_ids)
    )
    UNION
    SELECT 'category_ids', ARRAY(
        SELECT DISTINCT category_id::VARCHAR FROM product WHERE id = ANY(product_ids)
    )
    UNION
    SELECT 'min_and_max_price', ARRAY[
        (SELECT MIN(price)::VARCHAR FROM search_product WHERE id = ANY (product_ids)),
        (SELECT MAX(price)::VARCHAR FROM search_product WHERE id = ANY (product_ids))
    ];

$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION update_search_products() RETURNS void AS $$
    DELETE FROM search_product;

    INSERT INTO search_product
    SELECT 
        id, category_id, created_at, updated_at, is_hidden, available, archived, canonical_url_collection_id, 
        (SELECT MIN(price) FROM variant v WHERE v.product_id = product.id),
        (SELECT MIN(old_price) FROM variant v WHERE v.product_id = product.id),
        unit, ignore_discounts, title, description, currency_code,

        ARRAY(SELECT c.id FROM collection2product c2p JOIN collection c ON c2p.collection_id = c.id AND c2p.product_id = product.id WHERE NOT c.db_hidden),
        ARRAY(SELECT c.title FROM collection2product c2p JOIN collection c ON c2p.collection_id = c.id AND c2p.product_id = product.id WHERE NOT c.db_hidden),
        ARRAY(SELECT "position" FROM image i WHERE product_id = product.id AND NOT i.db_hidden),
        ARRAY(SELECT original_url FROM image i WHERE product_id = product.id AND NOT i.db_hidden),
        ARRAY(SELECT p.title FROM product2property p2p JOIN property p ON p2p.property_id = p.id AND p2p.product_id = product.id WHERE NOT p.db_hidden),
        ARRAY(SELECT p2p."value" FROM product2property p2p JOIN property p ON p2p.property_id = p.id AND p2p.product_id = product.id WHERE NOT p.db_hidden),
        ARRAY(SELECT p.title || ' ' || p2p."value" FROM product2property p2p JOIN property p ON p2p.property_id = p.id AND p2p.product_id = product.id WHERE NOT p.db_hidden
            UNION SELECT o_n.title || ' ' || ov."value" FROM
                variant v JOIN variant2option_value v2ov ON v.id = v2ov.variant_id AND v.product_id = product.id
                JOIN option_value ov ON v2ov.option_value_id = ov.id AND v2ov.variant_id = v.id
                JOIN option_name o_n ON ov.option_name_id = o_n.id)
    FROM product
    WHERE NOT product.db_hidden;
$$ LANGUAGE SQL;





-- ==== login / authorization ====

CREATE OR REPLACE FUNCTION add_guest_account(arg_email VARCHAR) RETURNS
void
AS $$
    INSERT INTO client (id, email, is_guest) VALUES (
        (SELECT
            CASE WHEN MIN(id) < 0 THEN MIN(id) - 1
            ELSE -1 END
        FROM client), 
        arg_email,
        TRUE
    );
$$ LANGUAGE SQL;

