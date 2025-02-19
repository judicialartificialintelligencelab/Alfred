import os
import re
import time
import requests
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text
from urllib.parse import urljoin
import random


# Use a custom User-Agent to mimic a real browser.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    )
}


# -------------------------------------------------------------------
# Helper function to extrude href from each <a> html element
def extrude_href(target_HTML=""):
    """
    Extract hrefs and category titles from <a> elements with class "link-secondary".
    """
    print("=== Extracting hrefs and titles from provided HTML ===")
    soup = BeautifulSoup(target_HTML, "html.parser")
    links = soup.find_all("a", class_="link-secondary")
    results = []
    for link in links:
        href = link.get("href")
        title = link.text.strip()
        results.append((href, title))
        print(f"  Extracted: href='{href}' | title='{title}'")
    return results


# -------------------------------------------------------------------
def get_year_links(html):
    soup = BeautifulSoup(html, "html.parser")
    year_links = []
    for link in soup.find_all("a", href=True):
        # Check both text and href for year patterns
        if re.search(r"\b(19|20)\d{2}\b", link.text) or re.search(
            r"\b(19|20)\d{2}\b", link["href"]
        ):
            year_links.append(link.get("href"))
    return year_links


def get_month_links(html):
    """
    Parse the given HTML and return a list of month links.
    This example uses a regex that matches month names.
    """
    print("=== Extracting month links ===")
    soup = BeautifulSoup(html, "html.parser")
    print(f"Month page HTML snippet (first 10 chars): {html[:10]}...")
    month_links = []
    for li in soup.find_all("li", class_="make-database"):
        link = li.find("a", href=True)
        if link and re.search(
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
            link.text,
            re.IGNORECASE,
        ):
            month_links.append(link.get("href"))
    return month_links


def get_case_links(html):
    soup = BeautifulSoup(html, "html.parser")
    case_links = []
    # Look for any element that could logically contain case links
    containers = soup.find_all(
        ["div", "ul", "ol", "table"], class_=re.compile(r"case-list|results")
    )
    for container in containers:
        for link in container.find_all("a", href=True):
            href = link["href"]
            if re.search(r"\d{4}/\d+\.html", href):
                case_links.append(href)
    return case_links


def get_rtf_link(html):
    soup = BeautifulSoup(html, "html.parser")
    # First, check for hrefs ending with .rtf
    rtf_anchor = soup.find("a", href=re.compile(r"\.rtf$", re.IGNORECASE))
    # If not found, check for "RTF" in link text
    if not rtf_anchor:
        rtf_anchor = soup.find("a", string=re.compile(r"\bRTF\b", re.IGNORECASE))
    # If still not found, check for "Download" or "Document" links
    if not rtf_anchor:
        rtf_anchor = soup.find(
            "a", href=re.compile(r"download|document", re.IGNORECASE)
        )
    return rtf_anchor.get("href") if rtf_anchor else None


# -------------------------------------------------------------------
def process_subdirectories(base_url="", extracted=None):
    """
    Process each category using the order given by the extracted (href, title) pairs.
    """

    print("Base URL:", base_url)
    print(f"Processing {len(extracted)} category links (by order).")
    for idx, (href, title) in enumerate(extracted):
        # Use urljoin to build the full URL.
        category_url = urljoin(base_url, href)
        print(f"\n=== Processing category URL: {category_url} ===")
        print(f"Category title: {title}")
        print(f"Assigned folder: {title}")

        # Use the target subdirectory directly for saving the file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        training_dir = os.path.dirname(script_dir)
        target_folder = os.path.join(training_dir, "data", title)
        os.makedirs(target_folder, exist_ok=True)  # Ensure folder exists

        # Ensure that the subdirectory already exists, no need to create it
        if not os.path.exists(target_folder):
            print(f"❌ Subdirectory does not exist: {target_folder}")
            continue

        # ----------------------------
        # Download the category page
        try:
            cat_response = requests.get(
                category_url, headers=HEADERS, allow_redirects=True
            )
            print(f"Response status: {cat_response.status_code}")
            if cat_response.status_code != 200:
                print(f"Failed to fetch category page: {category_url}")
                continue
            cat_html = cat_response.text
            print(f"Name: {category_url}")
            print(f"Category page HTML snippet (first 10 chars): {cat_html[:10]}...")
        except Exception as e:
            print(f"Error processing {category_url}: {e}")
            continue
        # ----------------------------

        # Now that the category page is downloaded, proceed with extracting year links.
        year_links = get_year_links(cat_html)
        if not year_links:
            print("❌ No year links found on category page.")
            continue

        for y_href in year_links:
            # Ensure the category URL ends with a slash
            category_base = (
                category_url if category_url.endswith("/") else category_url + "/"
            )
            year_url = (
                urljoin(category_url + "/", y_href)
                if not y_href.startswith("http")
                else y_href
            )
            print(f"Assigned folder: {title}")
            print(f"\n  === Processing year page: {year_url} ===")
            try:
                year_response = requests.get(year_url, headers=HEADERS)
                if year_response.status_code != 200:
                    print(f"  Failed to fetch year page: {year_url}")
                    continue
                year_html = year_response.text
                print(f"Year page HTML snippet (first 10 chars): {year_html[:10]}...")
            except Exception as e:
                print(f"  Error fetching year page {year_url}: {e}")
                continue

            # Extract month links from the year page.
            month_links = get_month_links(year_html)
            print(f"✅ Found month links: {month_links}")
            if not month_links:
                print("❌  No month links found on year page.")
                continue

            for file_href in month_links:
                # Ensure the year URL ends with a slash
                file_url = urljoin(year_url + "/", file_href)
                print(f"\n    === Processing case url: {file_url} ===")
                try:
                    file_response = requests.get(file_url, headers=HEADERS)
                    if file_response.status_code != 200:
                        print(f"    Failed to fetch case url: {file_url}")
                        continue
                    file_html = file_response.text
                    print(
                        f"✅ Case url HTML snippet (first 50 chars): {file_html[:50]}..."
                    )
                    # Extract the case name from the HTML <title> tag
                    soup = BeautifulSoup(file_html, "html.parser")
                    case_name = (
                        soup.title.string if soup.title else f"case_{idx}"
                    )  # Fallback if no title
                    case_name = re.sub(
                        r'[\/:*?"<>|]', "_", case_name
                    )  # Sanitize the case name
                    print(f"Extracted case name: {case_name}")

                    rtf_href = get_rtf_link(file_html)
                    if not rtf_href:
                        print("❌      No RTF link found on case page.")
                        continue
                    # KEY FIX: Use case_url as the base for urljoin, not base_url
                    rtf_url = urljoin(file_url, rtf_href)  # <-- CHANGE HERE
                    print(f"        Downloading RTF file: {rtf_url}")
                    try:
                        rtf_response = requests.get(rtf_url, headers=HEADERS)
                        print(
                            f"        RTF Response Status: {rtf_response.status_code}"
                        )
                        if rtf_response.status_code != 200:
                            print(f"        Failed to download RTF file: {rtf_url}")
                            continue
                        rtf_content = rtf_response.text
                        print(f"        RTF Content Length: {len(rtf_content)}")
                    except Exception as e:
                        print(f"        Error downloading RTF file {rtf_url}: {e}")
                        continue

                    try:
                        # Convert RTF to text
                        case_text = rtf_to_text(rtf_content)
                    except Exception as e:
                        print(f"        Error converting RTF to text: {e}")
                        continue

                    # Construct the case file name
                    case_id = (
                        re.search(r"\d+\.html$", file_url).group().replace(".html", "")
                    )
                    safe_case_id = f"case_{case_id}"
                    file_name = os.path.join(target_folder, f"{case_name}.txt")

                    # Write the case text to the file
                    try:
                        with open(file_name, "w", encoding="utf-8") as f:
                            f.write(case_text)
                        print(f"        Written file: {file_name}")
                    except Exception as e:
                        print(f"        Error writing file {file_name}: {e}")

                    # Add randomized delay between 1-3 seconds
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"    Error fetching file page {file_url}: {e}")
                    continue

    # End of processing one category.


# End of process_subdirectories()


def main():
    # Base URL for building absolute URLs
    base_url = "https://www.saflii.org"

    target_HTML = """<table class="table table-striped table-bordered rounded">
                    <tbody>
                    <tr><td><a href="/za/journals/ADRY" class="link-secondary">South Africa: African Disability Rights Yearbook </a></td></tr>
                    <tr><td><a href="/za/journals/AHRLJ" class="link-secondary">South Africa: African Human Rights Law Journal </a></td></tr>
                    <tr><td><a href="/za/journals/ALR" class="link-secondary">South Africa: African Law Review </a></td></tr>
                    <tr><td><a href="/za/cases/ZACAC" class="link-secondary">South Africa: Competition Appeal Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZACT" class="link-secondary">South Africa: Competition Tribunal</a></td></tr>
                    <tr><td><a href="/za/cases/ZACONAF" class="link-secondary">South Africa: Consumer Affairs Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZACGSO" class="link-secondary">South Africa: Consumer Goods and Services Ombud</a></td></tr>
                    <tr><td><a href="/za/cases/ZACC" class="link-secondary">South Africa: Constitutional Court</a></td></tr>
                    <tr><td><a href="/za/other/ZACCRolls" class="link-secondary">South Africa: Constitutional Court Rolls</a></td></tr>
                    <tr><td><a href="/za/cases/ZACCP" class="link-secondary">South Africa: Court of the Commissioner of Patents</a></td></tr>
                    <tr><td><a href="/za/cases/ZACOMMC" class="link-secondary">South Africa: Commercial Crime Court</a></td></tr>
                    <tr><td><a href="/za/journals/DEJURE" class="link-secondary">South Africa: <em>De Jure</em> Law Journal </a></td></tr>
                    <tr><td><a href="/za/journals/DEREBUS" class="link-secondary">South Africa: <em>DE REBUS</em>  </a></td></tr>
                    <tr><td><a href="/za/cases/ZAECBHC" class="link-secondary">South Africa: Eastern Cape High Court, Bhisho</a></td></tr>
                    <tr><td><a href="/za/other/ZAECBHCRolls" class="link-secondary">South Africa: Eastern Cape High Court Rolls, Bisho</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECGHC" class="link-secondary">South Africa: Eastern Cape High Court, Grahamstown</a></td></tr>
                    <tr><td><a href="/za/other/ZAECGHCRolls" class="link-secondary">South Africa: Eastern Cape High Court Rolls, Grahamstown</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECQBHC" class="link-secondary">South Africa: Eastern Cape High Court, Gqeberha</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECMKHC" class="link-secondary">South Africa: Eastern Cape High Court, Makhanda</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECMHC" class="link-secondary">South Africa: Eastern Cape High Court, Mthatha</a></td></tr>
                    <tr><td><a href="/za/other/ZAECMHCRolls" class="link-secondary">South Africa: Eastern Cape High Court Rolls, Mthatha</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECPEHC" class="link-secondary">South Africa: Eastern Cape High Court, Port Elizabeth</a></td></tr>
                    <tr><td><a href="/za/other/ZAECPEHCRolls" class="link-secondary">South Africa: Eastern Cape High Court Rolls, Port Elizabeth</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECELLC" class="link-secondary">South Africa: Eastern Cape High Court, East London Local Court</a></td></tr>
                    <tr><td><a href="/za/other/ZAECELLCRolls" class="link-secondary">South Africa: Eastern Cape High Court, East London Local Court Rolls</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAECPrGaz/" class="link-secondary">South Africa: Eastern Cape Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAEC" class="link-secondary">South Africa: Electoral Court </a></td></tr>
                    <tr><td><a href="/za/cases/ZAEQC" class="link-secondary">South Africa: Equality Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZAFSHC" class="link-secondary">South Africa: Free State High Court, Bloemfontein</a></td></tr>
                    <tr><td><a href="/za/other/ZAFSHCRolls" class="link-secondary">South Africa: Free State High Court Rolls, Bloemfontein</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAFSPrGaz/" class="link-secondary">South Africa: Free State Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAECHC" class="link-secondary">South Africa: High Courts - Eastern Cape</a></td></tr>
                    <tr><td><a href="/za/cases/ZAGPHC" class="link-secondary">South Africa: High Courts - Gauteng</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAGPPrGaz/" class="link-secondary">South Africa: Gauteng Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAKZHC" class="link-secondary">South Africa: High Courts - Kwazulu Natal</a></td></tr>
                    <tr><td><a href="/za/cases/ZAKZDHC" class="link-secondary">South Africa: Kwazulu-Natal High Court, Durban</a></td></tr>
                    <tr><td><a href="/za/other/ZAKZDHCRolls" class="link-secondary">South Africa: Kwazulu-Natal High Court Rolls, Durban</a></td></tr>
                    <tr><td><a href="/za/cases/ZAKZPHC" class="link-secondary">South Africa: Kwazulu-Natal High Court, Pietermaritzburg</a></td></tr>
                    <tr><td><a href="/za/other/ZAKZPHCRolls" class="link-secondary">South Africa: Kwazulu-Natal High Court Rolls, Pietermaritzburg</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAKZPrGaz/" class="link-secondary">South Africa: Kwazulu-Natal Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAIC" class="link-secondary">South Africa: Industrial Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZALAC" class="link-secondary">South Africa: Labour Appeal Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZALC" class="link-secondary">South Africa: Labour Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZALCCT" class="link-secondary">South Africa: Labour Court Cape Town </a></td></tr>
                    <tr><td><a href="/za/cases/ZALCJHB" class="link-secondary">South Africa: Labour Court Johannesburg </a></td></tr>
                    <tr><td><a href="/za/cases/ZALCPE" class="link-secondary">South Africa: Labour Court Port Elizabeth </a></td></tr>
                    <tr><td><a href="/za/cases/ZALCD" class="link-secondary">South Africa: Labour Court Durban </a></td></tr>
                    <tr><td><a href="/za/cases/ZALCC" class="link-secondary">South Africa: Land Claims Court</a></td></tr>
                    <tr><td><a href="/za/journals/LDD" class="link-secondary">South Africa: Law, Democracy and Development Law Journal</a></td></tr>
                    <tr><td><a href="/za/other/ZALRC" class="link-secondary">South Africa: Law Reform Commission</a></td></tr>
                    <tr><td><a href="/za/cases/ZALMPPHC" class="link-secondary">South Africa: Limpopo High Court, Polokwane</a></td></tr>
                    <tr><td><a href="/za/other/ZALMPPHCRolls" class="link-secondary">South Africa: Limpopo High Court Rolls, Polokwane</a></td></tr>
                    <tr><td><a href="/za/cases/ZALMPTHC" class="link-secondary">South Africa: Limpopo High Court, Thohoyandou</a></td></tr>
                    <tr><td><a href="/za/other/ZALMPHCRolls" class="link-secondary">South Africa: Limpopo High Court Rolls, Thohoyandou</a></td></tr>
                    <tr><td><a href="/za/gaz/ZALMPrGaz/" class="link-secondary">South Africa: Limpopo Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAMPMBHC/" class="link-secondary">South Africa: Mbombela High Court, Mpumalanga</a></td></tr>
                    <tr><td><a href="/za/cases/ZAMPMHC/" class="link-secondary">South Africa: Middelburg High Court, Mpumalanga</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAMPPrGaz/" class="link-secondary">South Africa: Mpumalanga Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZANCT" class="link-secondary">South Africa: National Consumer Tribunal</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAGovGaz/" class="link-secondary">South Africa: National Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZANCHC" class="link-secondary">South Africa: Northern Cape High Court, Kimberley</a></td></tr>
                    <tr><td><a href="/za/other/ZANCHCRolls" class="link-secondary">South Africa: Northern Cape High Court Rolls, Kimberley</a></td></tr>
                    <tr><td><a href="/za/gaz/ZANCPrGaz/" class="link-secondary">South Africa: Northern Cape Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/cases/ZAGPPHC" class="link-secondary">South Africa: North Gauteng High Court, Pretoria</a></td></tr>
                    <tr><td><a href="/za/other/ZAGPPHCRolls" class="link-secondary">South Africa: North Gauteng High Court Rolls, Pretoria</a></td></tr>
                    <tr><td><a href="/za/cases/ZANWHC" class="link-secondary">South Africa: North West Consumer Affairs Court, Mafikeng</a></td></tr>
                    <tr><td><a href="/za/cases/ZANWHC" class="link-secondary">South Africa: North West High Court, Mafikeng</a></td></tr>
                    <tr><td><a href="/za/other/ZANWHCRolls" class="link-secondary">South Africa: North West High Court Rolls, Mafikeng</a></td></tr>
                    <tr><td><a href="/za/gaz/ZANWPrGaz/" class="link-secondary">South Africa: North West Provincial Government Gazettes</a></td></tr>
                    <tr><td><a href="/za/journals/PER" class="link-secondary">South Africa: Potchefstroom Electronic Law Journal // Potchefstroomse Elektroniese Regsblad </a></td></tr>
                    <tr><td><a href="/za/other/ZARC" class="link-secondary">South Africa: Rules of Superior Courts</a></td></tr>
                    <tr><td><a href="/za/cases/ZARMC" class="link-secondary">South Africa: Rules of Magistrates Courts</a></td></tr>
                    <tr><td><a href="/za/cases/ZAGPJHC" class="link-secondary">South Africa: South Gauteng High Court, Johannesburg</a></td></tr>
                    <tr><td><a href="/za/other/ZAGPJHCRolls" class="link-secondary">South Africa: South Gauteng High Court Rolls, Johannesburg</a></td></tr>
                    <tr><td><a href="/za/cases/ZAST" class="link-secondary">South Africa: Special Tribunal</a></td></tr>
                    <tr><td><a href="/za/other/ZASTRolls" class="link-secondary">South Africa: Special Tribunal Court Rolls</a></td></tr>
                    <tr><td><a href="/za/cases/ZASCA" class="link-secondary">South Africa: Supreme Court of Appeal</a></td></tr>
                    <tr><td><a href="/za/other/ZASCARolls" class="link-secondary">South Africa: Supreme Court of Appeal Court Rolls</a></td></tr>
                    <tr><td><a href="/za/cases/ZATC" class="link-secondary">South Africa: Tax Court</a></td></tr>
                    <tr><td><a href="/za/cases/ZAWT" class="link-secondary">South Africa: Water Tribunal</a></td></tr>
                    <tr><td><a href="/za/cases/ZAWCHC" class="link-secondary">South Africa: Western Cape High Court, Cape Town</a></td></tr>
                    <tr><td><a href="/za/other/ZAWCHCRolls" class="link-secondary">South Africa: Western Cape High Court Rolls, Cape Town</a></td></tr>
                    <tr><td><a href="/za/gaz/ZAWCPrGaz/" class="link-secondary">South Africa: Western Cape Provincial Government Gazettes</a></td></tr>
                    </tbody>
                  </table>"""

    print("=== Starting extraction of HREFs from provided table ===")
    extracted = extrude_href(target_HTML)
    process_subdirectories(base_url, extracted)


if __name__ == "__main__":
    main()
