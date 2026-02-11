FROM ghcr.io/zhayujie/chatgpt-on-wechat:latest

# Switch to root to install dependencies and copy files
USER root

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# This ensures new dependencies like sqlite-web are installed
RUN pip install --no-cache-dir -r requirements.txt

# Create the directory for the database and ensure permissions
RUN mkdir -p /app/channel/web && chown -R noroot:noroot /app/channel/web

# Switch back to non-root user for security
USER noroot

ENTRYPOINT ["/entrypoint.sh"]