# Torrent Downloader with ExpressVPN and Plex-Compatible Structure

---

## Project Overview
This project is a torrent downloader application designed for seamless media management and privacy. It leverages **qBittorrent**, **FastAPI**, and **ExpressVPN** to ensure your downloads are organized in a Plex-compatible format while maintaining security and anonymity.

---

## Key Features
- **VPN Protection**: Routes all torrent traffic through ExpressVPN to safeguard your privacy.
- **Plex-Compatible Organization**: Automatically organizes TV shows into directories (`Show Name/Season XX`) for easy Plex library integration.
- **Magnet Link Downloads**: Supports adding torrents via magnet links.
- **Sequential Downloads**: Enables sequential downloading for faster playback.
- **Lightweight API**: Provides a FastAPI-powered REST endpoint for adding new torrents.

---

## Technologies Used
- **Docker Compose**: Simplifies container orchestration.
- **FastAPI**: Backend framework for API implementation.
- **qBittorrent**: Torrent client for downloading and managing torrents.
- **ExpressVPN**: Ensures secure and private torrenting.

---

## Folder Structure
├── app/\
│ ├── Dockerfile # Dockerfile for the app container\
│ ├── start.sh # Entry point for the app container\
│ ├── requirements.txt # Python dependencies\
│ ├── main.py # FastAPI application code\
├── expressvpn/\
│ ├── Dockerfile # Dockerfile for the VPN container\
│ ├── files # Scripting files\
│ │ ├── activate.exp # Script to activate ExpressVPN\
│ │ ├── start.sh # Entry point for the VPN container\
├── docker-compose.yml # Docker Compose configuration file\
└── README.md # Documentation\


---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone --recurse-submodules https://github.com/PetersonGuo/PirateBayTorrenter.git
cd PirateBayTorrenter
```

### 2. Edit the docker-compose-example.yml file
Fill in the spots that say \<Enter xxx> with your own values and change the filename to ``docker-compose.yml``

### 3. Build and Start Services
Use Docker Compose to build and start the containers:

```bash
docker-compose up --build
```

### 4. API Usage
Once running, the Web API will be available at http://\<your-server-ip\>:8000. 

### 5. qbittorrent Usage
The qbittorrent website will be available at http://\<your-server-ip\>:8080. Login with the credentials used in the docker-compose file

## File Naming Requirements
The application expects TV show torrents to follow these naming conventions:
- `Show.Name.S02E01`
- `Show Name S02E01`
- `ShowNameS02E01`
- `Show.Name.S02`
- `Show Name S02`
- `ShowNameS02`

---

## Security Considerations
- **VPN Requirement**: Ensure the ExpressVPN container is running and healthy to avoid traffic leaks.
- **Port Exposure**: Don't expose any ports (e.g., `8000`) to the public. Use a tunnel to your local network.
- **Environment Variables**: Do not expose sensitive information like the ExpressVPN activation code in public repositories.

---

## Troubleshooting

1. **VPN Not Connecting**:
   - Check the ExpressVPN logs using:
     ```bash
     docker logs expressvpn
     ```
   - Ensure the activation code is valid and the container has access to `/dev/net/tun`.

2. **No Internet in App Container**:
   - Verify the `network_mode` in `docker-compose.yml` is set to `service:expressvpn`.

3. **API Not Responding**:
   - Ensure the FastAPI container is running:
     ```bash
     docker ps
     ```

---

## Future Enhancements
- **User Interface**: Add a web-based dashboard for managing torrents.
- **Episode Detection**: Improve parsing to identify and prioritize episodes for sequential downloading.
- **Multi-VPN Support**: Allow selection of VPN providers.
