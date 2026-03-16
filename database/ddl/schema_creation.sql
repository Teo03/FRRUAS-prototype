DROP SCHEMA IF EXISTS project CASCADE;
CREATE SCHEMA project;
SET search_path TO project;

CREATE TABLE user_types (
    type_id         SERIAL          PRIMARY KEY,
    type_name       VARCHAR(128)    NOT NULL UNIQUE,
    description     VARCHAR(256)    NOT NULL
);

CREATE TABLE users (
    user_id         SERIAL          PRIMARY KEY,
    first_name      VARCHAR(128)    NOT NULL,
    last_name       VARCHAR(128)    NOT NULL,
    email           VARCHAR(128)    NOT NULL UNIQUE,
    password        VARCHAR(128)    NOT NULL,
    type_id         INTEGER         NOT NULL REFERENCES user_types(type_id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(type_id);

CREATE TABLE resource_types (
    type_id         SERIAL          PRIMARY KEY,
    type_name       VARCHAR(128)    NOT NULL UNIQUE,
    is_physical     BOOLEAN         NOT NULL
);

CREATE TABLE locations (
    location_id     SERIAL          PRIMARY KEY,
    building        VARCHAR(128)    NOT NULL,
    room            VARCHAR(128)    NOT NULL,
    UNIQUE (building, room)
);

CREATE INDEX idx_locations_building ON locations(building);

CREATE TABLE resources (
    resource_id         SERIAL          PRIMARY KEY,
    name                VARCHAR(128)    NOT NULL,
    description         VARCHAR(512)    NOT NULL,
    available_from      TIME            NOT NULL DEFAULT '08:00',
    available_to        TIME            NOT NULL DEFAULT '20:00',
    available_weekends  BOOLEAN         NOT NULL DEFAULT FALSE,
    type_id             INTEGER         NOT NULL REFERENCES resource_types(type_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    location_id         INTEGER         NULL REFERENCES locations(location_id) ON UPDATE CASCADE ON DELETE SET NULL,
    CHECK (available_to > available_from)
);

CREATE INDEX idx_resources_type ON resources(type_id);
CREATE INDEX idx_resources_location ON resources(location_id);

CREATE TABLE reservations (
    reservation_id      SERIAL          PRIMARY KEY,
    start_time          TIMESTAMP       NOT NULL,
    end_time            TIMESTAMP       NOT NULL,
    status              VARCHAR(32)     NOT NULL DEFAULT 'pending',
    purpose             VARCHAR(512)    NOT NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recurrence_group_id UUID            NULL,
    user_id             INTEGER         NOT NULL REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    approved_by         INTEGER         NULL REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET NULL,
    resource_id         INTEGER         NOT NULL REFERENCES resources(resource_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (end_time > start_time),
    CHECK (status IN ('pending', 'approved', 'rejected', 'completed', 'cancelled'))
);

CREATE INDEX idx_reservations_user ON reservations(user_id);
CREATE INDEX idx_reservations_approver ON reservations(approved_by);
CREATE INDEX idx_reservations_resource ON reservations(resource_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_times ON reservations(start_time, end_time);
CREATE INDEX idx_reservations_recurrence ON reservations(recurrence_group_id) WHERE recurrence_group_id IS NOT NULL;
