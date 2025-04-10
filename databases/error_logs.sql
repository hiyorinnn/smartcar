-- Select the database
USE smartcar_logs;

-- Drop the table if it exists
DROP TABLE IF EXISTS error_logs;

-- Create the error_logs table
CREATE TABLE error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Log timestamp
    level VARCHAR(10) NOT NULL,                    -- ERROR, INFO, WARNING
    status_code INT,                               -- HTTP status code (e.g., 404, 500)
    message TEXT NOT NULL,                         -- Log message details
    client_ip VARCHAR(45) NOT NULL,                -- IP address of the request
    url VARCHAR(255) NOT NULL                      -- The requested URL
);

select * from error_logs;