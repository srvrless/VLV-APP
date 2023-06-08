CREATE TABLE search_product (
    id BIGINT PRIMARY KEY NOT NULL,
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
    property_values VARCHAR[],
    search_option_and_properties VARCHAR[]
);

CREATE INDEX idx_search_product_category_id ON search_product (category_id);   
CREATE INDEX idx_search_product_created_at ON search_product (created_at);   
CREATE INDEX idx_search_product_updated_at ON search_product (updated_at);   
CREATE INDEX idx_search_product_price ON search_product (price);   
CREATE INDEX idx_search_product_old_price ON search_product (old_price);   
CREATE INDEX idx_search_product_title ON search_product (title);   
CREATE INDEX idx_search_product_collection_ids ON search_product USING GIN(collection_ids);  
CREATE INDEX idx_search_product_collection_names ON search_product USING GIN(collection_names);  
CREATE INDEX idx_search_product_property_names ON search_product USING GIN(property_names);  
CREATE INDEX idx_search_product_property_values ON search_product USING GIN(property_values);  
CREATE INDEX idx_search_product_search_option_and_properties ON search_product USING GIN(search_option_and_properties);  

