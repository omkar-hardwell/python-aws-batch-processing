"""Application entry point."""
from flask_s3_uploads.app import app
from flask_s3_uploads.configs import DEBUG, PORT


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
