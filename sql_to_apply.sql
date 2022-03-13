UPDATE waste_manager_wastedata SET is_diverted = 'true' WHERE waste_category IN ('styrofoam', 'regulated-substances')
UPDATE waste_manager_Wastedata SET unit='mt' WHERE waste_category IN ('electronics', 'batteries', 'regulated-substances', 'general-waste', 'styrofoam');
UPDATE waste_manager_Wastedata SET unit='unit' WHERE waste_category IN ('writing-instruments', 'ink-toner', 'pallets');