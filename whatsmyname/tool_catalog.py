"""
RECON Tool Catalog — Master knowledge base of forensics & OSINT tools.

Each entry provides:
  - name / command / category / description
  - install_hint for macOS
  - input_types (what kind of data it operates on)
  - passive: whether the tool is non-intrusive
  - examples: 5+ real-world usage examples
  - works_well_with: tools to chain next, with reasoning
  - learn_more: documentation URL
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Category constants
# ---------------------------------------------------------------------------

CAT_OSINT_USERNAME = "OSINT / Username Enumeration"
CAT_OSINT_EMAIL = "OSINT / Email Intelligence"
CAT_OSINT_PHONE = "OSINT / Phone Intelligence"
CAT_OSINT_GENERAL = "OSINT / General Reconnaissance"
CAT_NETWORK = "Network Analysis & Capture"
CAT_DNS = "DNS & Domain Intelligence"
CAT_WEB = "Web Recon & Scraping"
CAT_METADATA = "Metadata & File Analysis"
CAT_STEGO = "Steganography"
CAT_CRYPTO = "Password Cracking & Crypto"
CAT_FORENSICS = "Digital Forensics & Recovery"
CAT_REVERSE = "Reverse Engineering & Binary Analysis"
CAT_TRAFFIC = "Traffic Interception & Proxy"
CAT_SYSINFO = "System & Process Inspection"
CAT_NETWORKING = "Networking Utilities"
CAT_FACE_RECOG = "Face Recognition & Image Intel"
CAT_RELATIONSHIP = "Relationship Investigation / SPOTLIGHT"

ALL_CATEGORIES = [
    CAT_OSINT_USERNAME, CAT_OSINT_EMAIL, CAT_OSINT_PHONE, CAT_OSINT_GENERAL,
    CAT_NETWORK, CAT_DNS, CAT_WEB, CAT_METADATA, CAT_STEGO, CAT_CRYPTO,
    CAT_FORENSICS, CAT_REVERSE, CAT_TRAFFIC, CAT_SYSINFO, CAT_NETWORKING,
    CAT_FACE_RECOG, CAT_RELATIONSHIP,
]


@dataclass
class CatalogEntry:
    name: str
    command: str
    category: str
    description: str
    install_hint: str
    input_types: list[str] = field(default_factory=list)
    passive: bool = True
    examples: list[dict] = field(default_factory=list)
    works_well_with: list[dict] = field(default_factory=list)
    learn_more: str = ""

    @property
    def installed(self) -> bool:
        return shutil.which(self.command) is not None

    @property
    def path(self) -> str | None:
        return shutil.which(self.command)


# ---------------------------------------------------------------------------
# The catalog
# ---------------------------------------------------------------------------

TOOL_CATALOG: list[CatalogEntry] = [

    # ===================================================================
    # OSINT / Username Enumeration
    # ===================================================================
    CatalogEntry(
        name="wmn",
        command="wmn",
        category=CAT_OSINT_USERNAME,
        description="WhatsMyName — checks usernames across 4,300+ websites using community-maintained JSON data.",
        install_hint="pip install whatsmyname",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "wmn johndoe", "desc": "Basic username search across all 4,300+ sites"},
            {"cmd": "wmn johndoe --output json --output-file results.json", "desc": "Export results as JSON for processing"},
            {"cmd": "wmn johndoe --output csv --output-file results.csv", "desc": "Export as CSV spreadsheet"},
            {"cmd": "wmn johndoe --no-banner --no-color | grep '✓'", "desc": "Quiet mode, pipe to grep for hits only"},
            {"cmd": "wmn johndoe --timeout 10", "desc": "Set per-site timeout to 10 seconds for faster scans"},
            {"cmd": "wmn johndoe --output html --output-file report.html", "desc": "Generate HTML report for sharing"},
        ],
        works_well_with=[
            {"tool": "sherlock", "reason": "Cross-validate username findings — different detection methods catch different sites"},
            {"tool": "maigret", "reason": "Maigret has deep parsing and can extract profile metadata wmn misses"},
            {"tool": "holehe", "reason": "Once you have a username, check if common email variants are registered anywhere"},
            {"tool": "h8mail", "reason": "Check if any email variants from this username appear in data breaches"},
        ],
        learn_more="https://github.com/WebBreacher/WhatsMyName",
    ),

    CatalogEntry(
        name="sherlock",
        command="sherlock",
        category=CAT_OSINT_USERNAME,
        description="Sherlock — hunt usernames across ~400 social networks with high accuracy.",
        install_hint="pip install sherlock-project",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "sherlock johndoe", "desc": "Search for username across all supported sites"},
            {"cmd": "sherlock johndoe --print-found", "desc": "Only print sites where the username was found"},
            {"cmd": "sherlock johndoe --json results.json", "desc": "Export results to JSON file"},
            {"cmd": "sherlock johndoe --timeout 15", "desc": "Set per-site timeout to 15 seconds"},
            {"cmd": "sherlock johndoe janedoe alice", "desc": "Search for multiple usernames in one run"},
            {"cmd": "sherlock johndoe --site twitter instagram github", "desc": "Only check specific sites"},
        ],
        works_well_with=[
            {"tool": "wmn", "reason": "wmn covers 10x more sites — use both for maximum coverage"},
            {"tool": "maigret", "reason": "Maigret extracts profile data (bio, links) that Sherlock doesn't"},
            {"tool": "social-analyzer", "reason": "Detects profiles using multiple methods including AI-based matching"},
            {"tool": "exiftool", "reason": "If you find profile photos, check them for EXIF metadata (GPS, camera info)"},
        ],
        learn_more="https://github.com/sherlock-project/sherlock",
    ),

    CatalogEntry(
        name="maigret",
        command="maigret",
        category=CAT_OSINT_USERNAME,
        description="Maigret — deep username search across ~3,000 sites with profile data extraction.",
        install_hint="pip install maigret",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "maigret johndoe", "desc": "Full search across 3,000+ sites"},
            {"cmd": "maigret johndoe -n 100", "desc": "Limit to top 100 most popular sites (faster)"},
            {"cmd": "maigret johndoe --timeout 15 -J simple", "desc": "Quick scan with JSON output"},
            {"cmd": "maigret johndoe --html report.html", "desc": "Generate interactive HTML report"},
            {"cmd": "maigret johndoe --pdf report.pdf", "desc": "Generate PDF report for documentation"},
            {"cmd": "maigret johndoe --tags dating,finance", "desc": "Only search sites with specific tags"},
        ],
        works_well_with=[
            {"tool": "sherlock", "reason": "Different detection engines — Sherlock catches sites Maigret misses and vice versa"},
            {"tool": "holehe", "reason": "Take discovered email patterns and check which services they're registered on"},
            {"tool": "theharvester", "reason": "Harvest additional emails and subdomains related to the target"},
            {"tool": "whois", "reason": "If domains are found, run whois to get registrant info"},
        ],
        learn_more="https://github.com/soxoj/maigret",
    ),

    CatalogEntry(
        name="social-analyzer",
        command="social-analyzer",
        category=CAT_OSINT_USERNAME,
        description="Social Analyzer — profile detection across 900+ sites using multiple analysis methods.",
        install_hint="pip install social-analyzer",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "social-analyzer --username johndoe --mode fast", "desc": "Fast scan across all sites"},
            {"cmd": "social-analyzer --username johndoe --output json", "desc": "Output as JSON for processing"},
            {"cmd": "social-analyzer --username johndoe --filter good", "desc": "Only show high-confidence matches"},
            {"cmd": "social-analyzer --username johndoe --method find", "desc": "Use find method (fastest)"},
            {"cmd": "social-analyzer --username johndoe --filter good,maybe --output json", "desc": "Show good and maybe matches as JSON"},
        ],
        works_well_with=[
            {"tool": "sherlock", "reason": "Cross-validate — different detection approaches yield different results"},
            {"tool": "nexfil", "reason": "NExfil sometimes finds profiles on niche sites social-analyzer misses"},
            {"tool": "exiftool", "reason": "Extract metadata from discovered profile images"},
        ],
        learn_more="https://github.com/qeeqbox/social-analyzer",
    ),

    CatalogEntry(
        name="socialscan",
        command="socialscan",
        category=CAT_OSINT_USERNAME,
        description="Socialscan — check username/email availability on major platforms via API queries.",
        install_hint="pip install socialscan",
        input_types=["username", "email"],
        passive=True,
        examples=[
            {"cmd": "socialscan johndoe", "desc": "Check if username is taken across major platforms"},
            {"cmd": "socialscan johndoe@gmail.com", "desc": "Check if email is registered on platforms"},
            {"cmd": "socialscan johndoe --json output.json", "desc": "Export availability data as JSON"},
            {"cmd": "socialscan user1 user2 user3", "desc": "Check multiple usernames at once"},
            {"cmd": "socialscan johndoe@gmail.com johndoe@yahoo.com", "desc": "Check multiple email variants"},
        ],
        works_well_with=[
            {"tool": "holehe", "reason": "Holehe checks registration on different set of services"},
            {"tool": "sherlock", "reason": "Socialscan confirms account existence, Sherlock provides profile URLs"},
            {"tool": "h8mail", "reason": "If email is registered somewhere, check if it's been in breaches"},
        ],
        learn_more="https://github.com/iojw/socialscan",
    ),

    CatalogEntry(
        name="nexfil",
        command="nexfil",
        category=CAT_OSINT_USERNAME,
        description="NExfil — OSINT username finder across social platforms and forums.",
        install_hint="pip install nexfil",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "nexfil -u johndoe", "desc": "Search for username across all platforms"},
            {"cmd": "nexfil -u johndoe -t 15", "desc": "Set 15-second timeout per site"},
            {"cmd": "nexfil -u johndoe -l johndoe.txt", "desc": "Save results to a file"},
            {"cmd": "nexfil -u johndoe -H", "desc": "Show HTTP response headers for investigation"},
            {"cmd": "nexfil -u johndoe -v", "desc": "Verbose mode — see all sites being checked"},
        ],
        works_well_with=[
            {"tool": "wmn", "reason": "wmn has the largest site database — use both for maximum coverage"},
            {"tool": "maigret", "reason": "Maigret extracts profile metadata that nexfil doesn't capture"},
            {"tool": "socialscan", "reason": "Confirm availability status on major platforms"},
        ],
        learn_more="https://github.com/thewhiteh4t/nexfil",
    ),

    # ===================================================================
    # OSINT / Email Intelligence
    # ===================================================================
    CatalogEntry(
        name="holehe",
        command="holehe",
        category=CAT_OSINT_EMAIL,
        description="Holehe — check which online services an email address is registered on (login forms).",
        install_hint="pip install holehe",
        input_types=["email"],
        passive=True,
        examples=[
            {"cmd": "holehe target@gmail.com", "desc": "Check which services this email is registered on"},
            {"cmd": "holehe target@gmail.com --only-used", "desc": "Only show services where email IS registered"},
            {"cmd": "holehe target@gmail.com --no-color", "desc": "Plain text output for piping/logging"},
            {"cmd": "holehe target@gmail.com --csv output.csv", "desc": "Export results as CSV"},
            {"cmd": "holehe target@gmail.com --only-used --no-clear", "desc": "Keep terminal clean, show only hits"},
        ],
        works_well_with=[
            {"tool": "h8mail", "reason": "Check if the email has appeared in data breaches"},
            {"tool": "socialscan", "reason": "Verify email registration on platforms holehe doesn't cover"},
            {"tool": "theharvester", "reason": "Find additional email addresses related to the same domain"},
            {"tool": "whois", "reason": "If the email uses a custom domain, whois the domain for registrant info"},
        ],
        learn_more="https://github.com/megadose/holehe",
    ),

    CatalogEntry(
        name="h8mail",
        command="h8mail",
        category=CAT_OSINT_EMAIL,
        description="h8mail — email breach data hunter. Checks if an email appears in known data breaches.",
        install_hint="pip install h8mail",
        input_types=["email"],
        passive=True,
        examples=[
            {"cmd": "h8mail -t target@gmail.com", "desc": "Search for email in public breach databases"},
            {"cmd": "h8mail -t target@gmail.com -o results.csv", "desc": "Export breach results to CSV"},
            {"cmd": "h8mail -t targets.txt", "desc": "Bulk search — one email per line in file"},
            {"cmd": "h8mail -t target@gmail.com -k config.ini", "desc": "Use API keys for premium breach sources"},
            {"cmd": "h8mail -t target@gmail.com --chase", "desc": "Chase mode — follow related emails found in breaches"},
        ],
        works_well_with=[
            {"tool": "holehe", "reason": "holehe shows which services the email uses, h8mail shows which leaked"},
            {"tool": "theharvester", "reason": "Find more email addresses to check for breaches"},
            {"tool": "sherlock", "reason": "If breaches reveal usernames, search for those usernames"},
        ],
        learn_more="https://github.com/khast3x/h8mail",
    ),

    CatalogEntry(
        name="theHarvester",
        command="theharvester",
        category=CAT_OSINT_GENERAL,
        description="theHarvester — gather emails, hosts, subdomains, and URLs from public sources.",
        install_hint="pip install theHarvester",
        input_types=["username", "email", "domain"],
        passive=True,
        examples=[
            {"cmd": "theharvester -d example.com -b all -l 100", "desc": "Harvest everything from all sources for a domain"},
            {"cmd": "theharvester -d johndoe -b duckduckgo,urlscan -l 50", "desc": "Search for a username using specific engines"},
            {"cmd": "theharvester -d example.com -b anubis,rapiddns -l 100", "desc": "Find subdomains using passive DNS sources"},
            {"cmd": "theharvester -d example.com -b hackertarget -f output.html", "desc": "Generate HTML report"},
            {"cmd": "theharvester -d example.com -b all -l 200 -f results", "desc": "Deep harvest with file output"},
        ],
        works_well_with=[
            {"tool": "nmap", "reason": "Scan discovered hosts and subdomains for open services"},
            {"tool": "whois", "reason": "Whois the discovered domains for registrant info"},
            {"tool": "dig", "reason": "Dig deeper into discovered DNS records"},
            {"tool": "holehe", "reason": "Check discovered email addresses for service registrations"},
            {"tool": "h8mail", "reason": "Check discovered emails against breach databases"},
        ],
        learn_more="https://github.com/laramies/theHarvester",
    ),

    # ===================================================================
    # OSINT / Phone Intelligence
    # ===================================================================
    CatalogEntry(
        name="phoneinfoga",
        command="phoneinfoga",
        category=CAT_OSINT_PHONE,
        description="PhoneInfoga — advanced phone number OSINT: carrier, line type, location, reputation.",
        install_hint="brew install phoneinfoga  # or download binary from GitHub releases",
        input_types=["phone"],
        passive=True,
        examples=[
            {"cmd": "phoneinfoga scan -n +15551234567", "desc": "Full scan of a US phone number"},
            {"cmd": "phoneinfoga scan -n +447911123456", "desc": "Scan a UK mobile number"},
            {"cmd": "phoneinfoga serve -p 8080", "desc": "Start web UI on port 8080 for interactive investigation"},
            {"cmd": "phoneinfoga scan -n +15551234567 --scanner all", "desc": "Run all available scanners"},
            {"cmd": "phoneinfoga scan -n '+1 (555) 123-4567'", "desc": "Works with formatted numbers too"},
        ],
        works_well_with=[
            {"tool": "ignorant", "reason": "Check which social platforms the phone number is registered on"},
            {"tool": "holehe", "reason": "If you find an associated email, check its registrations"},
            {"tool": "sherlock", "reason": "If you find an associated username, enumerate their profiles"},
        ],
        learn_more="https://github.com/sundowndev/phoneinfoga",
    ),

    CatalogEntry(
        name="ignorant",
        command="ignorant",
        category=CAT_OSINT_PHONE,
        description="Ignorant — check which social platforms a phone number is registered on.",
        install_hint="pip install ignorant",
        input_types=["phone"],
        passive=True,
        examples=[
            {"cmd": "ignorant +1 5551234567", "desc": "Check US number for social media registrations"},
            {"cmd": "ignorant +44 7911123456", "desc": "Check UK number"},
            {"cmd": "ignorant +1 5551234567 --only-used", "desc": "Only show platforms where number IS registered"},
            {"cmd": "ignorant +1 5551234567 --no-color", "desc": "Plain output for scripting"},
            {"cmd": "ignorant +33 612345678 --only-used --no-clear", "desc": "French number, clean output"},
        ],
        works_well_with=[
            {"tool": "phoneinfoga", "reason": "PhoneInfoga gives carrier/location data, Ignorant shows registrations"},
            {"tool": "holehe", "reason": "If you find an associated email through phone lookup, check its registrations"},
            {"tool": "sherlock", "reason": "If you discover a username from a phone account, enumerate profiles"},
        ],
        learn_more="https://github.com/megadose/ignorant",
    ),

    # ===================================================================
    # Network Analysis & Capture
    # ===================================================================
    CatalogEntry(
        name="nmap",
        command="nmap",
        category=CAT_NETWORK,
        description="Nmap — the gold standard network scanner. Discovers hosts, ports, services, and OS fingerprints.",
        install_hint="brew install nmap",
        input_types=["ip", "domain", "subnet"],
        passive=False,
        examples=[
            {"cmd": "nmap -sV 192.168.1.1", "desc": "Service/version detection on a single host"},
            {"cmd": "nmap -sn 192.168.1.0/24", "desc": "Ping sweep — discover all live hosts on a subnet"},
            {"cmd": "nmap -A -T4 target.com", "desc": "Aggressive scan: OS detection, scripts, traceroute"},
            {"cmd": "nmap -p 1-65535 -T4 192.168.1.1", "desc": "Full port scan (all 65K ports)"},
            {"cmd": "nmap --script vuln 192.168.1.1", "desc": "Run vulnerability detection scripts"},
            {"cmd": "nmap -sS -O 192.168.1.0/24 -oX scan.xml", "desc": "SYN scan + OS detection, XML output"},
            {"cmd": "nmap -Pn -p 80,443,8080 target.com", "desc": "Skip host discovery, scan specific web ports"},
        ],
        works_well_with=[
            {"tool": "tshark", "reason": "Capture the network traffic generated by nmap for deeper analysis"},
            {"tool": "curl", "reason": "Manually probe discovered web services for content"},
            {"tool": "whois", "reason": "Look up ownership info for discovered IPs"},
            {"tool": "dig", "reason": "Resolve hostnames found during scanning"},
            {"tool": "mitmproxy", "reason": "Intercept traffic to discovered web services for analysis"},
        ],
        learn_more="https://nmap.org/book/man.html",
    ),

    CatalogEntry(
        name="tshark",
        command="tshark",
        category=CAT_NETWORK,
        description="TShark — command-line Wireshark. Capture and analyze network packets from the terminal.",
        install_hint="brew install wireshark  # tshark comes bundled",
        input_types=["interface", "pcap"],
        passive=True,
        examples=[
            {"cmd": "tshark -i en0 -c 100", "desc": "Capture 100 packets on en0 (Wi-Fi) interface"},
            {"cmd": "tshark -r capture.pcap", "desc": "Read and display a saved capture file"},
            {"cmd": "tshark -i en0 -f 'tcp port 80' -c 50", "desc": "Capture only HTTP traffic"},
            {"cmd": "tshark -r capture.pcap -Y 'dns' -T fields -e dns.qry.name", "desc": "Extract DNS query names from a capture"},
            {"cmd": "tshark -i en0 -w output.pcap -a duration:60", "desc": "Capture all traffic for 60 seconds to file"},
            {"cmd": "tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri", "desc": "Extract HTTP requests (host + URI)"},
        ],
        works_well_with=[
            {"tool": "nmap", "reason": "Capture traffic during nmap scans to analyze what nmap sends/receives"},
            {"tool": "mitmproxy", "reason": "Intercept HTTPS traffic that tshark can't decrypt without keys"},
            {"tool": "tcpdump", "reason": "tcpdump for quick capture, tshark for deep analysis"},
            {"tool": "whois", "reason": "Look up IPs found in captured traffic"},
        ],
        learn_more="https://www.wireshark.org/docs/man-pages/tshark.html",
    ),

    CatalogEntry(
        name="tcpdump",
        command="tcpdump",
        category=CAT_NETWORK,
        description="tcpdump — lightweight packet capture. Quick and dirty network sniffing.",
        install_hint="brew install tcpdump  # usually pre-installed on macOS",
        input_types=["interface"],
        passive=True,
        examples=[
            {"cmd": "sudo tcpdump -i en0 -c 50", "desc": "Capture 50 packets on Wi-Fi interface"},
            {"cmd": "sudo tcpdump -i en0 -w capture.pcap", "desc": "Save capture to file for later analysis in Wireshark"},
            {"cmd": "sudo tcpdump -i en0 port 53", "desc": "Capture only DNS traffic"},
            {"cmd": "sudo tcpdump -i en0 host 192.168.1.100", "desc": "Capture traffic to/from specific host"},
            {"cmd": "sudo tcpdump -i en0 -A port 80", "desc": "Show HTTP traffic in ASCII (readable text)"},
            {"cmd": "sudo tcpdump -r capture.pcap 'tcp port 443'", "desc": "Read pcap and filter for HTTPS traffic"},
        ],
        works_well_with=[
            {"tool": "tshark", "reason": "Save with tcpdump, analyze deeply with tshark/Wireshark"},
            {"tool": "nmap", "reason": "Capture what nmap is doing on the wire"},
            {"tool": "strings", "reason": "Run strings on pcap files to find readable text in traffic"},
        ],
        learn_more="https://www.tcpdump.org/manpages/tcpdump.1.html",
    ),

    # ===================================================================
    # DNS & Domain Intelligence
    # ===================================================================
    CatalogEntry(
        name="whois",
        command="whois",
        category=CAT_DNS,
        description="Whois — query domain/IP registration data: owner, registrar, dates, contacts.",
        install_hint="Pre-installed on macOS",
        input_types=["domain", "ip"],
        passive=True,
        examples=[
            {"cmd": "whois example.com", "desc": "Look up domain registration info"},
            {"cmd": "whois 93.184.216.34", "desc": "Look up IP address ownership"},
            {"cmd": "whois -h whois.arin.net 93.184.216.34", "desc": "Query specific WHOIS server (ARIN for North America)"},
            {"cmd": "whois example.com | grep -i 'registrant\\|created\\|expires'", "desc": "Extract just registrant, creation, and expiry dates"},
            {"cmd": "whois example.com | grep -i 'name server'", "desc": "Find the authoritative name servers"},
        ],
        works_well_with=[
            {"tool": "dig", "reason": "After whois shows nameservers, dig their DNS records"},
            {"tool": "nmap", "reason": "Scan the IPs you find from whois"},
            {"tool": "theharvester", "reason": "Find emails and subdomains for the domain"},
            {"tool": "curl", "reason": "Visit discovered domains to see what's hosted"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/whois.1.html",
    ),

    CatalogEntry(
        name="dig",
        command="dig",
        category=CAT_DNS,
        description="dig — DNS lookup utility. Query any DNS record type for any domain.",
        install_hint="Pre-installed on macOS",
        input_types=["domain"],
        passive=True,
        examples=[
            {"cmd": "dig example.com", "desc": "Basic A record lookup"},
            {"cmd": "dig example.com MX", "desc": "Look up mail servers for a domain"},
            {"cmd": "dig example.com ANY", "desc": "Request all record types"},
            {"cmd": "dig +short example.com", "desc": "Short output — just the IP(s)"},
            {"cmd": "dig @8.8.8.8 example.com", "desc": "Query Google's DNS instead of default resolver"},
            {"cmd": "dig -x 93.184.216.34", "desc": "Reverse DNS lookup — IP to hostname"},
            {"cmd": "dig example.com TXT", "desc": "Check TXT records (SPF, DKIM, domain verification)"},
        ],
        works_well_with=[
            {"tool": "whois", "reason": "whois shows ownership, dig shows technical DNS configuration"},
            {"tool": "nslookup", "reason": "nslookup for quick checks, dig for detailed analysis"},
            {"tool": "nmap", "reason": "Resolve domains to IPs, then scan them"},
            {"tool": "theharvester", "reason": "Find subdomains, then dig each one"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/dig.1.html",
    ),

    CatalogEntry(
        name="nslookup",
        command="nslookup",
        category=CAT_DNS,
        description="nslookup — quick and simple DNS query tool. Good for fast lookups.",
        install_hint="Pre-installed on macOS",
        input_types=["domain", "ip"],
        passive=True,
        examples=[
            {"cmd": "nslookup example.com", "desc": "Quick DNS lookup for a domain"},
            {"cmd": "nslookup 93.184.216.34", "desc": "Reverse lookup — find hostname for an IP"},
            {"cmd": "nslookup -type=mx example.com", "desc": "Look up mail exchange records"},
            {"cmd": "nslookup example.com 8.8.8.8", "desc": "Query using Google's DNS server"},
            {"cmd": "nslookup -type=ns example.com", "desc": "Find authoritative nameservers"},
        ],
        works_well_with=[
            {"tool": "dig", "reason": "dig provides more detailed output and more options"},
            {"tool": "whois", "reason": "After finding IPs, check their ownership"},
            {"tool": "nmap", "reason": "Scan discovered hosts"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/nslookup.1.html",
    ),

    # ===================================================================
    # Metadata & File Analysis
    # ===================================================================
    CatalogEntry(
        name="exiftool",
        command="exiftool",
        category=CAT_METADATA,
        description="ExifTool — read, write, and manipulate metadata in images, documents, videos, and more.",
        install_hint="brew install exiftool",
        input_types=["file", "directory"],
        passive=True,
        examples=[
            {"cmd": "exiftool photo.jpg", "desc": "Display all metadata from a photo (GPS, camera, date, etc.)"},
            {"cmd": "exiftool -gps* photo.jpg", "desc": "Extract only GPS coordinates from an image"},
            {"cmd": "exiftool -r -ext jpg /path/to/photos/", "desc": "Recursively scan all JPGs in a directory"},
            {"cmd": "exiftool -all= photo.jpg", "desc": "STRIP all metadata from a file (privacy cleanup)"},
            {"cmd": "exiftool -csv -r /path/to/files/ > metadata.csv", "desc": "Export all metadata as CSV spreadsheet"},
            {"cmd": "exiftool -Google* document.pdf", "desc": "Check if document has Google Docs metadata"},
            {"cmd": "exiftool -Author -Creator *.docx", "desc": "Extract author/creator from all Word documents"},
        ],
        works_well_with=[
            {"tool": "strings", "reason": "Find hidden text in files that exiftool doesn't parse"},
            {"tool": "steghide", "reason": "If image has suspicious metadata, check for steganography"},
            {"tool": "file", "reason": "Verify the actual file type before running exiftool"},
            {"tool": "xxd", "reason": "Hex-inspect suspicious bytes exiftool reports"},
        ],
        learn_more="https://exiftool.org/",
    ),

    CatalogEntry(
        name="strings",
        command="strings",
        category=CAT_METADATA,
        description="strings — extract printable character sequences from binary files. Finds hidden text.",
        install_hint="Pre-installed on macOS",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "strings suspicious.exe", "desc": "Extract all readable strings from a binary"},
            {"cmd": "strings -n 10 firmware.bin", "desc": "Only show strings 10+ characters long (less noise)"},
            {"cmd": "strings malware.bin | grep -i 'http\\|url\\|password\\|key'", "desc": "Find URLs, passwords, keys in a binary"},
            {"cmd": "strings image.jpg | grep -i 'gps\\|location\\|date'", "desc": "Find embedded text in images"},
            {"cmd": "strings capture.pcap | grep -i 'user\\|pass\\|login'", "desc": "Extract credentials from network captures"},
            {"cmd": "strings -e l binary.bin", "desc": "Extract UTF-16 (little-endian) strings — common in Windows binaries"},
        ],
        works_well_with=[
            {"tool": "file", "reason": "Identify the file type before running strings"},
            {"tool": "xxd", "reason": "Hex dump suspicious regions found by strings"},
            {"tool": "exiftool", "reason": "For structured metadata extraction (exiftool) vs raw text (strings)"},
            {"tool": "objdump", "reason": "If strings reveals it's an executable, disassemble it"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/strings.1.html",
    ),

    CatalogEntry(
        name="file",
        command="file",
        category=CAT_METADATA,
        description="file — identify file type using magic bytes. Don't trust file extensions — verify with this.",
        install_hint="Pre-installed on macOS",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "file suspicious_doc.pdf", "desc": "Verify a 'PDF' is actually a PDF (could be disguised malware)"},
            {"cmd": "file *", "desc": "Identify types of all files in current directory"},
            {"cmd": "file -b photo.jpg", "desc": "Brief output — just the type, no filename"},
            {"cmd": "file -i document.docx", "desc": "Show MIME type (useful for web/forensics)"},
            {"cmd": "file -z archive.gz", "desc": "Peek inside compressed files"},
        ],
        works_well_with=[
            {"tool": "strings", "reason": "After identifying type, extract readable text"},
            {"tool": "exiftool", "reason": "After confirming image/document type, extract metadata"},
            {"tool": "xxd", "reason": "If file type is unexpected, inspect the raw hex bytes"},
            {"tool": "steghide", "reason": "If it's a JPEG/BMP, check for hidden data"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/file.1.html",
    ),

    CatalogEntry(
        name="xxd",
        command="xxd",
        category=CAT_METADATA,
        description="xxd — hex dump utility. Inspect raw bytes of any file. Essential for forensics.",
        install_hint="Pre-installed on macOS (comes with vim)",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "xxd suspicious.bin | head -50", "desc": "View first 50 lines of hex dump"},
            {"cmd": "xxd -l 256 file.dat", "desc": "Only show first 256 bytes"},
            {"cmd": "xxd -s 0x100 -l 64 file.bin", "desc": "Show 64 bytes starting at offset 0x100"},
            {"cmd": "xxd file.bin | grep -i '504b'", "desc": "Search for ZIP magic bytes (PK header)"},
            {"cmd": "xxd -r modified.hex > output.bin", "desc": "Convert hex dump BACK to binary (reverse)"},
            {"cmd": "xxd -i file.bin", "desc": "Output as C include file (for embedding in code)"},
        ],
        works_well_with=[
            {"tool": "file", "reason": "file identifies the type, xxd lets you see the raw magic bytes"},
            {"tool": "strings", "reason": "strings finds text, xxd shows surrounding byte context"},
            {"tool": "hexdump", "reason": "Alternative hex viewer with different formatting options"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/xxd.1.html",
    ),

    CatalogEntry(
        name="hexdump",
        command="hexdump",
        category=CAT_METADATA,
        description="hexdump — display file contents in hex, decimal, octal, or ASCII.",
        install_hint="Pre-installed on macOS",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "hexdump -C file.bin | head -30", "desc": "Canonical hex+ASCII dump (most common format)"},
            {"cmd": "hexdump -C -n 128 file.bin", "desc": "Only show first 128 bytes"},
            {"cmd": "hexdump -C -s 512 -n 64 disk.img", "desc": "Show 64 bytes starting at offset 512 (boot sector)"},
            {"cmd": "hexdump -C file.bin | grep 'JFIF\\|PNG\\|GIF8'", "desc": "Search for image headers in raw data"},
            {"cmd": "hexdump -v -e '/1 \"%02x \"' file.bin", "desc": "Custom format — space-separated hex bytes"},
        ],
        works_well_with=[
            {"tool": "xxd", "reason": "xxd can reverse hex to binary, hexdump is display-only"},
            {"tool": "file", "reason": "Identify file type to know what byte patterns to look for"},
            {"tool": "strings", "reason": "Combine: strings for text, hexdump for byte-level context"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/hexdump.1.html",
    ),

    # ===================================================================
    # Steganography
    # ===================================================================
    CatalogEntry(
        name="steghide",
        command="steghide",
        category=CAT_STEGO,
        description="Steghide — embed and extract hidden data in JPEG, BMP, WAV, and AU files.",
        install_hint="brew install steghide",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "steghide extract -sf secret.jpg", "desc": "Extract hidden data from a JPEG (prompts for passphrase)"},
            {"cmd": "steghide extract -sf secret.jpg -p ''", "desc": "Extract with empty passphrase (no password)"},
            {"cmd": "steghide info photo.jpg", "desc": "Check if a file contains embedded data without extracting"},
            {"cmd": "steghide embed -cf cover.jpg -ef secret.txt", "desc": "HIDE a text file inside a JPEG"},
            {"cmd": "steghide embed -cf cover.jpg -ef secret.txt -p 'mypassword'", "desc": "Hide with password protection"},
            {"cmd": "steghide extract -sf audio.wav -xf extracted.txt", "desc": "Extract hidden data from a WAV audio file"},
        ],
        works_well_with=[
            {"tool": "exiftool", "reason": "Check metadata first — steganography sometimes modifies EXIF data"},
            {"tool": "file", "reason": "Verify the file is actually a JPEG/BMP/WAV before running steghide"},
            {"tool": "strings", "reason": "Sometimes hidden data appears as readable strings in the file"},
            {"tool": "xxd", "reason": "Manually inspect byte patterns for signs of hidden data"},
        ],
        learn_more="https://steghide.sourceforge.net/documentation.php",
    ),

    # ===================================================================
    # Password Cracking & Crypto
    # ===================================================================
    CatalogEntry(
        name="john",
        command="john",
        category=CAT_CRYPTO,
        description="John the Ripper — password cracker supporting 200+ hash types. Cracks hashes offline.",
        install_hint="brew install john",
        input_types=["file", "hash"],
        passive=True,
        examples=[
            {"cmd": "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt", "desc": "Dictionary attack with rockyou wordlist"},
            {"cmd": "john --show hashes.txt", "desc": "Show already-cracked passwords"},
            {"cmd": "john --format=raw-md5 hashes.txt", "desc": "Crack MD5 hashes specifically"},
            {"cmd": "john --incremental hashes.txt", "desc": "Brute-force mode (tries all combinations)"},
            {"cmd": "john --rules --wordlist=words.txt hashes.txt", "desc": "Apply mangling rules to wordlist (password1 → P@ssword1!)"},
            {"cmd": "john --list=formats | grep -i sha", "desc": "List all supported hash formats containing 'sha'"},
            {"cmd": "zip2john protected.zip > zip_hash.txt && john zip_hash.txt", "desc": "Crack a password-protected ZIP file"},
        ],
        works_well_with=[
            {"tool": "strings", "reason": "Extract potential passwords from binary files for custom wordlists"},
            {"tool": "xxd", "reason": "Inspect hash files to verify format before cracking"},
            {"tool": "file", "reason": "Identify encrypted file types that john can extract hashes from"},
        ],
        learn_more="https://www.openwall.com/john/doc/",
    ),

    # ===================================================================
    # Digital Forensics & Recovery
    # ===================================================================
    CatalogEntry(
        name="testdisk",
        command="testdisk",
        category=CAT_FORENSICS,
        description="TestDisk — recover lost partitions, fix boot sectors, undelete files. Data recovery powerhouse.",
        install_hint="brew install testdisk",
        input_types=["device", "image"],
        passive=False,
        examples=[
            {"cmd": "testdisk /dev/disk2", "desc": "Interactive recovery mode on a disk (follow the menus)"},
            {"cmd": "testdisk disk_image.dd", "desc": "Analyze a forensic disk image"},
            {"cmd": "testdisk /list", "desc": "List all detected drives and partitions"},
            {"cmd": "photorec /dev/disk2", "desc": "PhotoRec (bundled) — recover deleted files by type"},
            {"cmd": "photorec disk.img", "desc": "Recover files from a disk image (photos, docs, etc.)"},
            {"cmd": "testdisk /log disk.img", "desc": "Run with logging for documentation"},
        ],
        works_well_with=[
            {"tool": "file", "reason": "Identify recovered files that may have lost their extensions"},
            {"tool": "exiftool", "reason": "Extract metadata from recovered images to establish timeline"},
            {"tool": "strings", "reason": "Search recovered files for specific keywords or evidence"},
            {"tool": "xxd", "reason": "Inspect recovered file headers to verify integrity"},
        ],
        learn_more="https://www.cgsecurity.org/wiki/TestDisk",
    ),

    # ===================================================================
    # Traffic Interception & Proxy
    # ===================================================================
    CatalogEntry(
        name="mitmproxy",
        command="mitmproxy",
        category=CAT_TRAFFIC,
        description="mitmproxy — interactive HTTPS proxy. Intercept, inspect, modify, and replay web traffic.",
        install_hint="brew install mitmproxy",
        input_types=["proxy"],
        passive=False,
        examples=[
            {"cmd": "mitmproxy", "desc": "Start interactive TUI proxy on port 8080"},
            {"cmd": "mitmweb", "desc": "Start web-based UI proxy (browser at http://127.0.0.1:8081)"},
            {"cmd": "mitmdump -w traffic.flow", "desc": "Dump all intercepted traffic to a file"},
            {"cmd": "mitmdump -r traffic.flow -n", "desc": "Read and display saved traffic"},
            {"cmd": "mitmdump --set block_global=false", "desc": "Allow connections from other devices on the network"},
            {"cmd": "mitmproxy --mode transparent", "desc": "Transparent proxy mode (no client config needed, requires routing setup)"},
        ],
        works_well_with=[
            {"tool": "tshark", "reason": "tshark sees encrypted traffic, mitmproxy decrypts it"},
            {"tool": "curl", "reason": "Use curl through mitmproxy: curl --proxy http://localhost:8080 URL"},
            {"tool": "nmap", "reason": "Discover services first, then intercept their traffic"},
        ],
        learn_more="https://docs.mitmproxy.org/stable/",
    ),

    # ===================================================================
    # Web Recon & Scraping
    # ===================================================================
    CatalogEntry(
        name="curl",
        command="curl",
        category=CAT_WEB,
        description="curl — transfer data to/from servers. The Swiss Army knife of HTTP requests.",
        install_hint="brew install curl  # macOS has it pre-installed but brew version is newer",
        input_types=["url"],
        passive=True,
        examples=[
            {"cmd": "curl -I https://example.com", "desc": "Fetch only HTTP headers (server type, tech stack)"},
            {"cmd": "curl -L https://bit.ly/shortlink", "desc": "Follow redirects to find the final URL"},
            {"cmd": "curl -s https://api.example.com/users | python3 -m json.tool", "desc": "Pretty-print API JSON response"},
            {"cmd": "curl -o page.html https://example.com", "desc": "Save page source to a file"},
            {"cmd": "curl -x socks5://127.0.0.1:9050 https://check.torproject.org", "desc": "Make request through Tor SOCKS proxy"},
            {"cmd": "curl -A 'Mozilla/5.0' -H 'Accept-Language: en' https://example.com", "desc": "Custom User-Agent and headers"},
        ],
        works_well_with=[
            {"tool": "dig", "reason": "Resolve the domain first, then curl the IP directly"},
            {"tool": "whois", "reason": "Whois the domain to understand who you're talking to"},
            {"tool": "mitmproxy", "reason": "Route curl through mitmproxy for inspection"},
            {"tool": "tshark", "reason": "Capture the traffic curl generates for analysis"},
        ],
        learn_more="https://curl.se/docs/manpage.html",
    ),

    CatalogEntry(
        name="wget",
        command="wget",
        category=CAT_WEB,
        description="wget — download files and mirror websites from the command line.",
        install_hint="brew install wget",
        input_types=["url"],
        passive=True,
        examples=[
            {"cmd": "wget https://example.com/file.pdf", "desc": "Download a single file"},
            {"cmd": "wget -r -l 2 -np https://example.com/", "desc": "Mirror a website (depth 2, no parent)"},
            {"cmd": "wget -i urls.txt", "desc": "Download all URLs listed in a file"},
            {"cmd": "wget --mirror --convert-links https://example.com/", "desc": "Full site mirror for offline analysis"},
            {"cmd": "wget -q --show-progress https://example.com/large.iso", "desc": "Quiet mode with progress bar"},
            {"cmd": "wget --user-agent='Googlebot' https://example.com/", "desc": "Download as Googlebot (see what bots see)"},
        ],
        works_well_with=[
            {"tool": "exiftool", "reason": "Download files, then extract their metadata"},
            {"tool": "strings", "reason": "Search downloaded files for interesting text"},
            {"tool": "curl", "reason": "curl for headers/API, wget for bulk downloads"},
        ],
        learn_more="https://www.gnu.org/software/wget/manual/",
    ),

    # ===================================================================
    # Reverse Engineering & Binary Analysis
    # ===================================================================
    CatalogEntry(
        name="objdump",
        command="objdump",
        category=CAT_REVERSE,
        description="objdump — display information about object files. Disassemble binaries.",
        install_hint="Pre-installed on macOS (Xcode CLT)",
        input_types=["file"],
        passive=True,
        examples=[
            {"cmd": "objdump -d binary", "desc": "Disassemble all executable sections"},
            {"cmd": "objdump -t binary", "desc": "Show symbol table (function names, variables)"},
            {"cmd": "objdump -h binary", "desc": "Show section headers (text, data, bss sizes)"},
            {"cmd": "objdump -s -j .rodata binary", "desc": "Dump contents of read-only data section"},
            {"cmd": "objdump --macho -d binary", "desc": "Disassemble macOS Mach-O binary"},
        ],
        works_well_with=[
            {"tool": "strings", "reason": "Extract readable text before deep disassembly"},
            {"tool": "file", "reason": "Identify binary format (ELF, Mach-O, PE) before disassembling"},
            {"tool": "lldb", "reason": "Dynamic debugging after static analysis with objdump"},
            {"tool": "xxd", "reason": "Hex inspect specific sections found by objdump"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/objdump.1.html",
    ),

    CatalogEntry(
        name="lldb",
        command="lldb",
        category=CAT_REVERSE,
        description="LLDB — the LLVM debugger. Debug programs, inspect memory, step through code.",
        install_hint="Pre-installed on macOS (Xcode CLT)",
        input_types=["file", "process"],
        passive=True,
        examples=[
            {"cmd": "lldb ./program", "desc": "Start debugging a program"},
            {"cmd": "lldb -p 12345", "desc": "Attach to a running process by PID"},
            {"cmd": "lldb -- ./program arg1 arg2", "desc": "Debug with command-line arguments"},
            {"cmd": "(lldb) breakpoint set --name main", "desc": "Set breakpoint at main function"},
            {"cmd": "(lldb) register read", "desc": "Read all CPU registers at current breakpoint"},
        ],
        works_well_with=[
            {"tool": "objdump", "reason": "Static analysis with objdump, dynamic with lldb"},
            {"tool": "dtrace", "reason": "System-level tracing while debugging with lldb"},
            {"tool": "strings", "reason": "Find interesting strings to search for in memory during debugging"},
        ],
        learn_more="https://lldb.llvm.org/use/tutorial.html",
    ),

    # ===================================================================
    # System & Process Inspection
    # ===================================================================
    CatalogEntry(
        name="lsof",
        command="lsof",
        category=CAT_SYSINFO,
        description="lsof — list open files. See what files/sockets/pipes every process has open.",
        install_hint="Pre-installed on macOS",
        input_types=["system"],
        passive=True,
        examples=[
            {"cmd": "lsof -i :8080", "desc": "Find what process is using port 8080"},
            {"cmd": "lsof -i -P -n", "desc": "List all network connections (no DNS resolution for speed)"},
            {"cmd": "lsof -u username", "desc": "List all files open by a specific user"},
            {"cmd": "lsof -p 12345", "desc": "List all files open by a specific process"},
            {"cmd": "lsof +D /path/to/directory", "desc": "Find processes accessing files in a directory"},
            {"cmd": "lsof -i TCP:443 -s TCP:ESTABLISHED", "desc": "Show all established HTTPS connections"},
        ],
        works_well_with=[
            {"tool": "netstat", "reason": "netstat shows network connections, lsof shows which process owns them"},
            {"tool": "dtrace", "reason": "After finding suspicious processes, trace their system calls"},
            {"tool": "tshark", "reason": "Capture traffic from suspicious connections found by lsof"},
        ],
        learn_more="https://man7.org/linux/man-pages/man8/lsof.8.html",
    ),

    CatalogEntry(
        name="netstat",
        command="netstat",
        category=CAT_SYSINFO,
        description="netstat — display network connections, routing tables, and interface statistics.",
        install_hint="Pre-installed on macOS",
        input_types=["system"],
        passive=True,
        examples=[
            {"cmd": "netstat -an | grep LISTEN", "desc": "Show all listening ports on the system"},
            {"cmd": "netstat -an | grep ESTABLISHED", "desc": "Show all active connections"},
            {"cmd": "netstat -rn", "desc": "Show routing table (where traffic goes)"},
            {"cmd": "netstat -s", "desc": "Show protocol statistics (packets sent/received/errors)"},
            {"cmd": "netstat -an | grep ':443'", "desc": "Find all HTTPS connections"},
        ],
        works_well_with=[
            {"tool": "lsof", "reason": "lsof shows which process owns each connection"},
            {"tool": "nmap", "reason": "After seeing what's listening, scan for more detail"},
            {"tool": "tshark", "reason": "Capture traffic on suspicious connections"},
        ],
        learn_more="https://man7.org/linux/man-pages/man8/netstat.8.html",
    ),

    CatalogEntry(
        name="dtrace",
        command="dtrace",
        category=CAT_SYSINFO,
        description="DTrace — dynamic tracing framework. Trace system calls, I/O, and kernel events in real-time.",
        install_hint="Pre-installed on macOS (requires SIP adjustment for some probes)",
        input_types=["system", "process"],
        passive=True,
        examples=[
            {"cmd": "sudo dtrace -n 'syscall:::entry { @[execname] = count(); }'", "desc": "Count syscalls per process"},
            {"cmd": "sudo dtrace -n 'syscall::open:entry { printf(\"%s %s\", execname, copyinstr(arg0)); }'", "desc": "Trace file opens by all processes"},
            {"cmd": "sudo dtrace -n 'proc:::exec-success { trace(curpsinfo->pr_psargs); }'", "desc": "Log every new process that starts"},
            {"cmd": "sudo dtrace -n 'syscall::write:entry /pid == 12345/ { @[arg0] = count(); }'", "desc": "Count writes by file descriptor for a specific PID"},
            {"cmd": "sudo dtruss -p 12345", "desc": "dtruss wrapper — trace syscalls of a running process (like strace)"},
        ],
        works_well_with=[
            {"tool": "lsof", "reason": "Find suspicious processes with lsof, trace them with dtrace"},
            {"tool": "lldb", "reason": "Debug + trace simultaneously for deep analysis"},
        ],
        learn_more="https://dtrace.org/guide/preface.html",
    ),

    # ===================================================================
    # Networking Utilities
    # ===================================================================
    CatalogEntry(
        name="nc",
        command="nc",
        category=CAT_NETWORKING,
        description="Netcat — the 'TCP/IP Swiss Army knife'. Connect, listen, transfer data, port scan.",
        install_hint="Pre-installed on macOS",
        input_types=["ip", "port"],
        passive=False,
        examples=[
            {"cmd": "nc -zv target.com 80", "desc": "Check if port 80 is open on target"},
            {"cmd": "nc -zv target.com 20-100", "desc": "Scan ports 20-100 on target"},
            {"cmd": "nc -l 4444", "desc": "Listen on port 4444 (receive connections)"},
            {"cmd": "echo 'test' | nc target.com 80", "desc": "Send data to a port"},
            {"cmd": "nc -l 4444 > received_file.bin", "desc": "Listen and save received data to file"},
        ],
        works_well_with=[
            {"tool": "nmap", "reason": "nmap for comprehensive scanning, nc for quick checks and interaction"},
            {"tool": "tshark", "reason": "Capture traffic generated by netcat connections"},
            {"tool": "ncat", "reason": "ncat (from nmap) has SSL support and more features"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/ncat.1.html",
    ),

    CatalogEntry(
        name="ncat",
        command="ncat",
        category=CAT_NETWORKING,
        description="Ncat — improved netcat from nmap. Supports SSL, proxies, and connection brokering.",
        install_hint="brew install nmap  # ncat comes bundled",
        input_types=["ip", "port"],
        passive=False,
        examples=[
            {"cmd": "ncat --ssl target.com 443", "desc": "Connect to HTTPS port with SSL"},
            {"cmd": "ncat -l -p 4444 --ssl", "desc": "Listen with SSL encryption"},
            {"cmd": "ncat --proxy 127.0.0.1:8080 target.com 80", "desc": "Connect through an HTTP proxy"},
            {"cmd": "ncat -l -p 4444 --exec /bin/bash", "desc": "Create a reverse shell listener (pen-testing)"},
            {"cmd": "ncat -zv target.com 1-1000", "desc": "Quick port scan of first 1000 ports"},
        ],
        works_well_with=[
            {"tool": "nmap", "reason": "nmap discovers services, ncat lets you manually interact with them"},
            {"tool": "nc", "reason": "Use nc for basic tasks, ncat when you need SSL or proxy support"},
            {"tool": "mitmproxy", "reason": "Route ncat through mitmproxy for traffic inspection"},
        ],
        learn_more="https://nmap.org/ncat/guide/",
    ),

    CatalogEntry(
        name="traceroute",
        command="traceroute",
        category=CAT_NETWORKING,
        description="traceroute — map the network path to a destination. Shows every router hop.",
        install_hint="Pre-installed on macOS",
        input_types=["domain", "ip"],
        passive=True,
        examples=[
            {"cmd": "traceroute example.com", "desc": "Trace the route to a domain"},
            {"cmd": "traceroute -n 8.8.8.8", "desc": "Trace without DNS resolution (faster)"},
            {"cmd": "traceroute -m 20 example.com", "desc": "Set max hops to 20"},
            {"cmd": "traceroute -T -p 443 example.com", "desc": "TCP traceroute on HTTPS port (bypasses some firewalls)"},
            {"cmd": "traceroute -I example.com", "desc": "Use ICMP instead of UDP (like Windows tracert)"},
        ],
        works_well_with=[
            {"tool": "whois", "reason": "Whois the intermediate IPs to see which networks the traffic crosses"},
            {"tool": "nmap", "reason": "Scan interesting hops discovered during traceroute"},
            {"tool": "dig", "reason": "Reverse-lookup IPs seen in traceroute hops"},
        ],
        learn_more="https://man7.org/linux/man-pages/man1/traceroute.1.html",
    ),

    CatalogEntry(
        name="ping",
        command="ping",
        category=CAT_NETWORKING,
        description="ping — test connectivity and measure latency to a host using ICMP echo.",
        install_hint="Pre-installed on macOS",
        input_types=["domain", "ip"],
        passive=True,
        examples=[
            {"cmd": "ping -c 5 example.com", "desc": "Send 5 pings to test if host is up"},
            {"cmd": "ping -c 10 -i 0.5 example.com", "desc": "10 pings, 0.5 seconds apart (fast check)"},
            {"cmd": "ping -s 1500 example.com", "desc": "Send large packets to test MTU/fragmentation"},
            {"cmd": "ping -t 5 example.com", "desc": "Set TTL to 5 (will fail if more than 5 hops)"},
            {"cmd": "ping -c 1 -W 2 192.168.1.1", "desc": "Quick connectivity check with 2-second timeout"},
        ],
        works_well_with=[
            {"tool": "traceroute", "reason": "If ping fails, traceroute shows where connectivity breaks"},
            {"tool": "nmap", "reason": "If host responds to ping, scan it for services"},
            {"tool": "dig", "reason": "If ping resolves to unexpected IP, investigate DNS"},
        ],
        learn_more="https://man7.org/linux/man-pages/man8/ping.8.html",
    ),

    # ===================================================================
    # Relationship Investigation / SPOTLIGHT
    # ===================================================================
    CatalogEntry(
        name="blackbird",
        command="blackbird",
        category=CAT_RELATIONSHIP,
        description="Blackbird — search usernames across 600+ sites including dating platforms, social media, and forums.",
        install_hint="git clone https://github.com/p1ngul1n0/blackbird.git",
        input_types=["username", "email"],
        passive=True,
        examples=[
            {"cmd": "blackbird --username johndoe", "desc": "Search username across 600+ sites"},
            {"cmd": "blackbird --username johndoe --json", "desc": "Export results as JSON"},
            {"cmd": "blackbird --email johndoe@gmail.com", "desc": "Search by email address"},
            {"cmd": "blackbird --username johndoe --filter dating", "desc": "Filter results to dating sites only"},
            {"cmd": "blackbird --username johndoe --pdf report.pdf", "desc": "Generate PDF report of findings"},
        ],
        works_well_with=[
            {"tool": "sherlock", "reason": "Sherlock uses different detection — combine for max coverage"},
            {"tool": "cupidcr4wl", "reason": "Blackbird finds profiles, cupidcr4wl checks adult/dating platforms specifically"},
            {"tool": "holehe", "reason": "Check discovered emails for service registrations"},
            {"tool": "toutatis", "reason": "Extract contact info from Instagram profiles found by Blackbird"},
        ],
        learn_more="https://github.com/p1ngul1n0/blackbird",
    ),

    CatalogEntry(
        name="cupidcr4wl",
        command="cupidcr4wl",
        category=CAT_RELATIONSHIP,
        description="Cupidcr4wl — crawls adult content and dating platforms for username/phone presence.",
        install_hint="git clone https://github.com/OSINTI4L/cupidcr4wl.git",
        input_types=["username", "phone"],
        passive=True,
        examples=[
            {"cmd": "cupidcr4wl -u johndoe", "desc": "Search username on adult/dating platforms"},
            {"cmd": "cupidcr4wl -p +15551234567", "desc": "Search phone number on dating platforms"},
            {"cmd": "cupidcr4wl -u johndoe -o results.json", "desc": "Export results to JSON"},
            {"cmd": "cupidcr4wl -u johndoe -v", "desc": "Verbose mode — show all checks"},
            {"cmd": "cupidcr4wl -u johndoe --timeout 30", "desc": "Extended timeout for slow platforms"},
        ],
        works_well_with=[
            {"tool": "blackbird", "reason": "Blackbird covers mainstream sites, cupidcr4wl covers adult/dating"},
            {"tool": "maigret", "reason": "Use maigret --tags dating for additional dating site coverage"},
            {"tool": "holehe", "reason": "Check if email is registered on hookup/dating services"},
            {"tool": "ignorant", "reason": "Check phone number registrations on messaging platforms"},
        ],
        learn_more="https://github.com/OSINTI4L/cupidcr4wl",
    ),

    # ===================================================================
    # Face Recognition & Image Intel
    # ===================================================================
    CatalogEntry(
        name="compreface",
        command="compreface",
        category=CAT_FACE_RECOG,
        description="CompreFace — self-hosted face recognition service. Detect, recognize, and verify faces via Docker + REST API.",
        install_hint="Bundled with RECON (requires Docker Desktop)",
        input_types=["file", "image"],
        passive=True,
        examples=[
            {"cmd": "compreface start", "desc": "Start the CompreFace Docker containers"},
            {"cmd": "compreface detect photo.jpg", "desc": "Detect all faces in a photo"},
            {"cmd": "compreface recognize suspect.jpg", "desc": "Recognize faces against known subjects"},
            {"cmd": "compreface verify face1.jpg face2.jpg", "desc": "Compare two faces for similarity"},
            {"cmd": "compreface add-subject --name 'John Doe' --image ref.jpg", "desc": "Add a known face to the database"},
            {"cmd": "compreface detect ./evidence_photos/ -o json", "desc": "Batch detect faces, export as JSON"},
            {"cmd": "compreface status", "desc": "Check if the service is running and healthy"},
        ],
        works_well_with=[
            {"tool": "exiftool", "reason": "Extract GPS/timestamp metadata from photos before face recognition"},
            {"tool": "sherlock", "reason": "Once you identify a person, search for their online presence"},
            {"tool": "maigret", "reason": "Deep username search for identified persons"},
            {"tool": "blackbird", "reason": "Search dating/social platforms for identified persons"},
            {"tool": "toutatis", "reason": "Extract contact info from Instagram profiles of matched faces"},
        ],
        learn_more="https://github.com/exadel-inc/CompreFace",
    ),

    # ===================================================================
    # OSINT / General Reconnaissance (additional)
    # ===================================================================
    CatalogEntry(
        name="untappd-scraper",
        command="untappd-scraper",
        category=CAT_OSINT_GENERAL,
        description="untappdScraper — scrape Untappd.com for drinking patterns, geolocation, friend networks, and venue history.",
        install_hint="Bundled with RECON (pip deps: bs4, geocoder, gmplot, googlemaps)",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "untappd-scraper -u targetuser", "desc": "Full profile scrape with patterns and venues"},
            {"cmd": "untappd-scraper -u targetuser --recent", "desc": "Only dump recent check-in locations"},
        ],
        works_well_with=[
            {"tool": "sherlock", "reason": "Find the Untappd username on other platforms"},
            {"tool": "maigret", "reason": "Deep search across 3,000+ sites for the same username"},
            {"tool": "exiftool", "reason": "Check photos posted alongside check-ins for GPS metadata"},
            {"tool": "blackbird", "reason": "Cross-reference on dating/social platforms"},
        ],
        learn_more="https://github.com/WebBreacher/untappdScraper",
    ),

    CatalogEntry(
        name="osint-tools-cli",
        command="osint-tools-cli",
        category=CAT_OSINT_GENERAL,
        description="OSINT Tools CLI — interactive TUI browser for 1,000+ OSINT tools and resources from Cipher387's collection.",
        install_hint="Bundled with RECON (requires Rust toolchain for building)",
        input_types=["system"],
        passive=True,
        examples=[
            {"cmd": "osint-tools-cli launch", "desc": "Start the interactive TUI browser"},
            {"cmd": "osint-tools-cli build", "desc": "Build from Rust source code"},
        ],
        works_well_with=[
            {"tool": "wmn", "reason": "Discover new tools to complement your WMN searches"},
            {"tool": "sherlock", "reason": "Find alternative tools for username enumeration"},
        ],
        learn_more="https://github.com/Coordinate-Cat/osint-tools-cli",
    ),

    # ===================================================================
    # Digital Forensics & Recovery (additional)
    # ===================================================================
    CatalogEntry(
        name="4n6notebooks",
        command="4n6notebooks",
        category=CAT_FORENSICS,
        description="4n6notebooks — Jupyter forensic notebooks for iOS: SQLCipher decrypt, Signal parsing, ProtonMail recovery, chat rendering.",
        install_hint="Bundled with RECON (pip deps: jupyterlab, pycryptodome, pandas, pgpy)",
        input_types=["file", "device"],
        passive=True,
        examples=[
            {"cmd": "4n6notebooks launch", "desc": "Open the full forensics lab in JupyterLab"},
            {"cmd": "4n6notebooks launch signal", "desc": "Open the iOS Signal parsing notebook"},
            {"cmd": "4n6notebooks launch sqlcipher", "desc": "Open the SQLCipher decryption notebook"},
            {"cmd": "4n6notebooks launch protonmail", "desc": "Open the ProtonMail recovery notebook"},
            {"cmd": "4n6notebooks list", "desc": "List all available forensic notebooks"},
            {"cmd": "4n6notebooks export signal --format html", "desc": "Export a completed notebook to HTML"},
        ],
        works_well_with=[
            {"tool": "keychain-decrypt", "reason": "Get encryption keys from iOS keychain to decrypt app databases"},
            {"tool": "exiftool", "reason": "Extract metadata from recovered media files"},
            {"tool": "strings", "reason": "Find interesting text in binary database files"},
            {"tool": "testdisk", "reason": "Recover deleted files from device images"},
            {"tool": "compreface", "reason": "Run face recognition on extracted photos"},
        ],
        learn_more="https://github.com/studiawan/4n6notebooks",
    ),

    CatalogEntry(
        name="keychain-decrypt",
        command="keychain-decrypt",
        category=CAT_FORENSICS,
        description="iOS Keychain Decrypter — decrypt saved passwords, WiFi creds, app tokens, and certificates from jailbroken iOS devices.",
        install_hint="Bundled with RECON (requires jailbroken device + Xcode for agent)",
        input_types=["device"],
        passive=False,
        examples=[
            {"cmd": "keychain-decrypt decrypt", "desc": "Run the full keychain decryption workflow"},
            {"cmd": "keychain-decrypt build-agent", "desc": "Compile the on-device key unwrapper agent"},
            {"cmd": "keychain-decrypt upload-agent", "desc": "Upload the agent to the jailbroken device"},
            {"cmd": "keychain-decrypt download-db", "desc": "Download keychain database from device"},
            {"cmd": "keychain-decrypt install-deps", "desc": "Install Python dependencies"},
        ],
        works_well_with=[
            {"tool": "4n6notebooks", "reason": "Use extracted keys to decrypt app databases in notebooks"},
            {"tool": "holehe", "reason": "Check extracted emails for service registrations"},
            {"tool": "h8mail", "reason": "Check extracted emails against breach databases"},
            {"tool": "sherlock", "reason": "Search extracted usernames across platforms"},
        ],
        learn_more="https://github.com/nicolo/ios_keychain_decrypter",
    ),

    CatalogEntry(
        name="toutatis",
        command="toutatis",
        category=CAT_RELATIONSHIP,
        description="Toutatis — Instagram OSINT. Extracts emails, phone numbers, and profile data from Instagram accounts.",
        install_hint="pip install toutatis",
        input_types=["username"],
        passive=True,
        examples=[
            {"cmd": "toutatis -u johndoe -s SESSION_ID", "desc": "Extract profile info (email, phone) from Instagram"},
            {"cmd": "toutatis -u johndoe -s SESSION_ID -j", "desc": "Output as JSON"},
            {"cmd": "toutatis -u johndoe -s SESSION_ID --proxy http://proxy:8080", "desc": "Route through proxy"},
            {"cmd": "toutatis -u janedoe -s SESSION_ID", "desc": "Check partner's Instagram for hidden contact info"},
            {"cmd": "toutatis -u username -s SESSION_ID -j > ig_data.json", "desc": "Save full profile data to file"},
        ],
        works_well_with=[
            {"tool": "holehe", "reason": "Use extracted email to check service registrations"},
            {"tool": "h8mail", "reason": "Check extracted email in breach databases"},
            {"tool": "sherlock", "reason": "Search for the Instagram username on other platforms"},
            {"tool": "exiftool", "reason": "Download and check profile photos for GPS metadata"},
        ],
        learn_more="https://github.com/megadose/toutatis",
    ),
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_all_entries() -> list[CatalogEntry]:
    """Return all catalog entries."""
    return TOOL_CATALOG


def get_entry(name: str) -> CatalogEntry | None:
    """Look up a tool by name (case-insensitive)."""
    name_lower = name.lower()
    for entry in TOOL_CATALOG:
        if entry.name.lower() == name_lower or entry.command.lower() == name_lower:
            return entry
    return None


def get_by_category(category: str | None = None) -> dict[str, list[CatalogEntry]]:
    """Group catalog entries by category. Optionally filter to one category."""
    cats: dict[str, list[CatalogEntry]] = {}
    for entry in TOOL_CATALOG:
        if category and entry.category != category:
            continue
        cats.setdefault(entry.category, []).append(entry)
    return dict(sorted(cats.items()))


def get_installed() -> list[CatalogEntry]:
    """Return only entries where the tool is installed on this system."""
    return [e for e in TOOL_CATALOG if e.installed]


def get_missing() -> list[CatalogEntry]:
    """Return entries where the tool is NOT installed."""
    return [e for e in TOOL_CATALOG if not e.installed]


def get_suggestions_for(tool_name: str) -> list[dict]:
    """Get 'works_well_with' suggestions for a specific tool."""
    entry = get_entry(tool_name)
    if entry is None:
        return []
    # Filter to only suggest tools that are actually installed
    suggestions = []
    for s in entry.works_well_with:
        companion = get_entry(s["tool"])
        installed = companion.installed if companion else False
        suggestions.append({
            **s,
            "installed": installed,
            "install_hint": companion.install_hint if companion and not installed else None,
        })
    return suggestions
