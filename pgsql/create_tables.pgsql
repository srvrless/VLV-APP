
-- DROP TABLE customers;

DROP TABLE client;
DROP TABLE client_group;
DROP TABLE address;
DROP TABLE collection2product;
DROP TABLE product2property;
DROP TABLE property;
DROP TABLE variant2option_value;
DROP TABLE variant;
DROP TABLE image;
DROP TABLE product;
DROP TABLE option_value;
DROP TABLE option_name;
DROP TABLE category;
DROP TABLE collection;


CREATE TABLE collection (
    id BIGINT PRIMARY KEY NOT NULL,
    parent_id BIGINT,
    title VARCHAR,
    description TEXT,
    "position" BIGINT,
    is_hidden BOOLEAN,
    is_smart BOOLEAN,
    db_hidden BOOLEAN DEFAULT FALSE
); 
CREATE INDEX idx_collection_title ON collection(title);

 
CREATE TABLE category (
    id BIGINT PRIMARY KEY NOT NULL,
    parent_id BIGINT,
    title VARCHAR,
    "position" BIGINT,
    db_hidden BOOLEAN DEFAULT FALSE
); 
CREATE INDEX idx_category_title ON category(title);


CREATE TABLE option_name (
    id BIGINT PRIMARY KEY NOT NULL,
    "position" INT,
    navigational BOOLEAN,
    title VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE
); 
CREATE INDEX idx_option_name_title ON option_name(title);


CREATE TABLE option_value (
    id BIGINT PRIMARY KEY NOT NULL,
    option_name_id BIGINT,
    "position" INT,
    "value" VARCHAR,
    image_url VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE
); 
CREATE INDEX idx_option_value_option_name_id ON option_value(option_name_id);
CREATE INDEX idx_option_value_value ON option_value(value);
 

CREATE TABLE product (
    id BIGINT PRIMARY KEY NOT NULL,
    category_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_hidden BOOLEAN,
    available BOOLEAN,
    archived BOOLEAN,
    canonical_url_collection_id BIGINT,
    unit VARCHAR,
    ignore_discounts BOOLEAN,
    title VARCHAR,
    description TEXT,
    currency_code VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category(id)
); 
CREATE INDEX idx_product_category_id ON product(category_id);
CREATE INDEX idx_product_created_at ON product(created_at);
CREATE INDEX idx_product_updated_at ON product(updated_at);
CREATE INDEX idx_product_title ON product(title);

CREATE TABLE image (
    id BIGINT PRIMARY KEY NOT NULL,
    product_id BIGINT,
    position INT,
    original_url VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(id)
); 
CREATE INDEX idx_image_product_id ON image(product_id);


CREATE TABLE variant (
    id BIGINT PRIMARY KEY NOT NULL,
    title VARCHAR,
    product_id BIGINT,
    sku VARCHAR,
    available BOOLEAN,
    image_id BIGINT,
    weight REAL,
    quantity INT,
    quantities_at_warehouses INT[],
    cost_price DECIMAL(20, 2),
    cost_price_in_site_currency DECIMAL(20, 2),
    price_in_site_currency DECIMAL(20, 2),
    base_price DECIMAL(20, 2),
    old_price DECIMAL(20, 2),
    price DECIMAL(20, 2),
    base_price_in_site_currency DECIMAL(20, 2),
    old_price_in_site_currency DECIMAL(20, 2),
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(id),
    CONSTRAINT fk_image FOREIGN KEY (image_id) REFERENCES image(id)
); 
CREATE INDEX idx_variant_title ON variant(title);
CREATE INDEX idx_variant_product_id ON variant(product_id);
CREATE INDEX idx_variant_cost_price ON variant(cost_price);
CREATE INDEX idx_variant_cost_price_in_site_currency ON variant(cost_price_in_site_currency);
CREATE INDEX idx_variant_price_in_site_currency ON variant(price_in_site_currency);
CREATE INDEX idx_variant_base_price ON variant(base_price);
CREATE INDEX idx_variant_old_price ON variant(old_price);
CREATE INDEX idx_variant_price ON variant(price);
CREATE INDEX idx_variant_base_price_in_site_currency ON variant(base_price_in_site_currency);
CREATE INDEX idx_variant_old_price_in_site_currency ON variant(old_price_in_site_currency);



CREATE TABLE variant2option_value (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    variant_id BIGINT,
    option_value_id BIGINT,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_variant FOREIGN KEY (variant_id) REFERENCES variant(id),
    CONSTRAINT fk_option_value FOREIGN KEY (option_value_id) REFERENCES option_value(id)
); 
CREATE INDEX idx_variant2option_value_variant_id ON variant2option_value(variant_id);
CREATE INDEX idx_variant2option_value_option_value_id ON variant2option_value(option_value_id);
    
 
CREATE TABLE property (
    id BIGINT PRIMARY KEY NOT NULL,
    "position" INT,
    is_hidden BOOLEAN,
    is_navigational BOOLEAN,
    title VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE
); 
CREATE INDEX idx_property_title ON property(title);


CREATE TABLE product2property (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    property_id BIGINT,
    product_id BIGINT,
    "value" VARCHAR,
    "position" INT,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_property FOREIGN KEY (property_id) REFERENCES property(id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(id)
); 
CREATE INDEX idx_product2property_property_id ON product2property(property_id);
CREATE INDEX idx_product2property_product_id ON product2property(product_id);
CREATE INDEX idx_product2property_value ON product2property("value");


CREATE TABLE collection2product (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    collection_id BIGINT,
    product_id BIGINT,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_collection FOREIGN KEY (collection_id) REFERENCES collection(id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(id)
); 
CREATE INDEX idx_collection2product_collection_id ON collection2product(collection_id);
CREATE INDEX idx_collection2product_product_id ON collection2product(product_id);


CREATE TABLE address (
    id BIGINT PRIMARY KEY NOT NULL,
    phone VARCHAR,
    full_locality_name VARCHAR,
    full_delivery_address VARCHAR,
    address_for_gis VARCHAR,
    location_valid BOOLEAN,
    address VARCHAR,
    country VARCHAR,
    state VARCHAR,
    city VARCHAR,
    zip VARCHAR,
    kladr_code VARCHAR,
    kladr_zip VARCHAR,
    region_zip VARCHAR,
    area VARCHAR,
    area_type VARCHAR,
    settlement VARCHAR,
    settlement_type VARCHAR,
    street VARCHAR,
    street_type VARCHAR,
    house VARCHAR,
    flat VARCHAR,
    is_kladr BOOLEAN,
    latitude VARCHAR,
    longitude VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE
);

CREATE TABLE client_group (
    id BIGINT PRIMARY KEY NOT NULL,
    title VARCHAR,
    discount VARCHAR,
    discount_description VARCHAR,
    is_default BOOLEAN,
    db_hidden BOOLEAN DEFAULT FALSE
);

CREATE TABLE client (
    id BIGINT PRIMARY KEY NOT NULL,
    email VARCHAR,
    is_guest BOOLEAN DEFAULT FALSE,
    name VARCHAR,
    phone VARCHAR,
    registered BOOLEAN,
    client_group_id BIGINT,
    surname VARCHAR,
    middlename VARCHAR,
    bonus_points BIGINT,
    "type" VARCHAR,
    contact_name VARCHAR,
    ip_addr VARCHAR,
    birth_date VARCHAR,
    default_address_id BIGINT,
    full_name VARCHAR,
    db_hidden BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_client_group FOREIGN KEY (client_group_id) REFERENCES client_group(id),
    CONSTRAINT fk_default_address FOREIGN KEY (default_address_id) REFERENCES address(id)
);
CREATE INDEX idx_client_email ON client(email);




-- CREATE TABLE customers (
--     id BIGSERIAL PRIMARY KEY NOT NULL,
--     name VARCHAR,
--     surname VARCHAR,
--     middlename VARCHAR,

--     birth_date VARCHAR,
--     city VARCHAR,

--     email VARCHAR,
--     email_accept VARCHAR,
--     "password" BYTEA,
--     phone VARCHAR,
--     phone_accept VARCHAR,

--     billing_history VARCHAR,
--     wishlist VARCHAR
-- );


-- CREATE TABLE products (
--     id BIGINT PRIMARY KEY NOT NULL,
--     available VARCHAR,
--     category_id BIGINT,
--     material VARCHAR,
--     colour VARCHAR,
--     brand VARCHAR,
--     size VARCHAR,
--     price DECIMAL(15, 2),
--     title VARCHAR,
--     description TEXT,
--     variants_id BIGINT[],
--     collections_ids BIGINT[],
--     images VARCHAR[]
-- );


-- CREATE TABLE wishlist (
--     id BIGSERIAL PRIMARY KEY NOT NULL,
--     customer_id BIGINT,
--     product_id BIGINT,
--     CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
--     CONSTRAINT fk_products FOREIGN KEY (product_id) REFERENCES products(id),
--     UNIQUE(customer_id, product_id)
-- );

-- CREATE TABLE cart (
--     id BIGSERIAL PRIMARY KEY NOT NULL,
--     customer_id BIGINT,
--     product_id BIGINT,
--     size REAL,
--     variant_id BIGINT,
--     amount BIGINT,
--     CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
--     CONSTRAINT fk_products FOREIGN KEY (product_id) REFERENCES products(id),
--     UNIQUE(customer_id, product_id)
-- );

-- CREATE TABLE images (
--     id BIGSERIAL PRIMARY KEY NOT NULL,
--     product_id BIGINT,
--     "position" BIGINT,
--     title VARCHAR,
--     original_url VARCHAR,
--     CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id)
-- );



