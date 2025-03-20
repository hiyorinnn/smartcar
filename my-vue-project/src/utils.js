import axios from "axios";

const errorServiceUrl = "http://localhost:5002/log_error";

export function logError(errorType, message) {
    return axios
        .post(
            errorServiceUrl,
            { error_type: errorType, message: message },
            {
                headers: {
                    "Content-Type": "application/json"  // Ensure correct content type is set
                }
            }
        )
        .then(response => {
            console.log("Error logged successfully:", response.data);  // Optionally log success
        })
        .catch(err => {
            console.error("Failed to log error:", err);  // Log any failure in the logging process
        });
}
