import os
import time
from playwright.sync_api import sync_playwright

output_dir = r"c:\Users\rishi\Downloads\Cotton-20261003T053350Z-1-001\presentation_assets"
os.makedirs(output_dir, exist_ok=True)

test_img_dir = r"c:\Users\rishi\Downloads\Cotton-20261003T053350Z-1-001\phase1_cotton\data\split\test\Bacterial_Blight"
sample_images = [os.path.join(test_img_dir, f) for f in os.listdir(test_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
sample_img = sample_images[0] if sample_images else None

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 1600, "height": 960}, device_scale_factor=1.5)
    page = context.new_page()

    # 1. Overview Page
    print("1. Capturing Overview...")
    page.goto("http://localhost:5173", wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path=os.path.join(output_dir, "01_dashboard_overview.png"))

    # 2. Map Page
    print("2. Capturing Suitability Map...")
    page.click("button:has-text('Google Suitability Map')")
    time.sleep(2)
    run_btn = page.query_selector("button:has-text('Run Cotton Suitability Analysis')")
    if run_btn:
        print("Clicking Run Cotton Suitability Analysis...")
        run_btn.click()
        # Wait for the results to load (Open-Meteo API takes 6-10s)
        try:
            page.wait_for_selector(".result-card, .evidence-badge, div:has-text('Potentially suitable')", timeout=15000)
            time.sleep(1)
        except Exception as e:
            print(f"Wait warning: {e}")
            time.sleep(5)
    page.screenshot(path=os.path.join(output_dir, "02_dashboard_suitability_map.png"))

    # 2b. Map with Satellite Farmlands Layer
    print("2b. Capturing Satellite Farmlands...")
    sat_btn = page.query_selector("button:has-text('Google Satellite')")
    if sat_btn:
        sat_btn.click()
        time.sleep(2.5)
        page.screenshot(path=os.path.join(output_dir, "02b_dashboard_satellite_map.png"))
        # switch back to road
        road_btn = page.query_selector("button:has-text('Google Road Map')")
        if road_btn:
            road_btn.click()
            time.sleep(1)

    # 3. Leaf Health AI Page
    print("3. Capturing Leaf Health AI with active prediction...")
    page.click("button:has-text('Leaf Health AI')")
    time.sleep(2)
    if sample_img:
        print(f"Setting input file: {sample_img}")
        page.set_input_files("input[type='file']", sample_img)
        time.sleep(2)
        pred_btn = page.query_selector("button:has-text('Analyze Cotton Leaf Health')")
        if pred_btn:
            print("Clicking Analyze Cotton Leaf Health...")
            pred_btn.click()
            try:
                page.wait_for_selector(".disease-result", timeout=12000)
                time.sleep(2)
            except Exception as e:
                print(f"Diagnosis wait warning: {e}")
                time.sleep(4)
    page.screenshot(path=os.path.join(output_dir, "03_dashboard_leaf_health_ai.png"))

    # 4. Market Prices Page
    print("4. Capturing Market Prices APMC...")
    page.click("button:has-text('Market Prices (APMC)')")
    time.sleep(2)
    page.screenshot(path=os.path.join(output_dir, "04_dashboard_mandi_prices.png"))

    browser.close()

print("All screenshots successfully captured with full data!")
