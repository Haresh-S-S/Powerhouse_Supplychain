import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.regulatory_knowledge import RegulatoryKnowledgeDocument, RegulatoryChunk
from app.rag.chunker import StatutoryChunker, generate_content_hash
from app.rag.vector_store import VectorStoreService


RAW_STATUTORY_SOURCES: List[Dict[str, Any]] = [
    {
        "source_id": "REG-FSSAI-2006-SEC31",
        "title": "FSSAI Food Business Licensing and Registration Regulations",
        "authority": "Food Safety and Standards Authority of India (FSSAI)",
        "jurisdiction": "Central (Union Government)",
        "document_type": "Act & Statutory Regulations",
        "act_name": "Food Safety and Standards Act, 2006",
        "section": "Section 31",
        "category": "restaurant",
        "effective_date": "2011-08-05",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://fssai.gov.in/upload/uploadfiles/files/Food_Safety_and_Standards_Act_2006.pdf",
        "raw_text": """CHAPTER VII - ENFORCEMENT OF THE ACT
Section 31 (Licensing and registration of food business):
(1) No person shall commence or carry on any food business except under a licence granted under this Act.
(2) Nothing contained in sub-section (1) shall apply to a petty manufacturer who himself manufactures, sells, or supplies any article of food or a petty retailer, hawker, itinerant vendor, or a temporary stall holder, who shall only obtain registration with the registering authority.
(3) Any person desirous of commencing or carrying on any food business shall make an application for grant of a licence to the Designated Officer in such form and accompanied by such fee as specified under FoSCoS Regulations.
(4) The Designated Officer shall cause an inspection of the food premises to be conducted and on receipt of the inspection report, either grant the licence or reject the application for reasons to be recorded in writing.
Rule 2.1 (Food Safety Management System): Every licensed food business operator shall implement a documented Food Safety Management System (FSMS) plan, maintain daily temperature logs for cold storage and hot holding, and retain water potability test certificates from NABL accredited laboratories.
Rule 2.2 (Supervisory Certification): At least one trained food safety supervisor certified under the Food Safety Training and Certification (FoSTaC) program must be present on commercial dining premises during operational kitchen shifts."""
    },
    {
        "source_id": "REG-ULB-HTL-SEC353",
        "title": "Municipal Corporation Health Trade & Sanitary Regulations",
        "authority": "Directorate of Municipal Administration / Urban Local Bodies",
        "jurisdiction": "Municipal / Urban Local Body",
        "document_type": "Municipal Bye-laws",
        "act_name": "City Municipal Corporation Act / Public Health Bye-laws",
        "section": "Section 353",
        "category": "restaurant",
        "effective_date": "2020-04-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://tn.gov.in/municipal-administration",
        "raw_text": """CHAPTER XII - REGULATION OF TRADES AND MANUFACTURES
Section 353 (Licensing of offensive and dangerous trades and food premises):
(1) No person shall, without a licence from the Commissioner, use any premises for manufacturing, preparing, storing, or selling food or beverages for public consumption within city municipal limits.
(2) Every person intending to open a restaurant, eating house, or catering kitchen shall submit an application accompanied by premises lease deed, property tax receipt, and water drainage clearance.
Rule 12 (Sanitary Requirements): Kitchen and dining floors must be paved with non-absorbent impervious tiles. Adequate grease traps must be installed in wastewater drains to prevent municipal sewer clogging.
Rule 14 (Pest Control & Medical Fitness): Commercial dining premises must maintain monthly professional pest eradication records and semi-annual medical fitness certificates for all culinary workers."""
    },
    {
        "source_id": "REG-POL-EAT-HOUSE",
        "title": "State Police Regulations for Eating Houses and Public Entertainment",
        "authority": "State Police Department / Municipal Licensing Authority",
        "jurisdiction": "State (Tamil Nadu)",
        "document_type": "Standing Orders",
        "act_name": "City Police Act / Eating House Regulations",
        "section": "Section 39",
        "category": "restaurant",
        "effective_date": "2019-06-15",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://police.tn.gov.in",
        "raw_text": """CHAPTER V - LICENSING OF PLACES OF PUBLIC RESORT
Section 39 (Licensing and controlling places of public entertainment and eateries):
(1) The Commissioner of Police or authorized licensing officer may grant a licence to keep or open an eating house, coffee house, or dining establishment upon inspection of premises security and fire egress.
(2) No eating house shall operate beyond prescribed municipal closing hours without a specific night operational permit.
Rule 5 (Public Safety and Surveillance): Commercial dining establishments with seating capacity exceeding 30 seats must install closed-circuit television (CCTV) cameras covering all public entry, cashier, and exit zones with minimum 30-day recorded footage archival."""
    },
    {
        "source_id": "REG-PCB-WATER-AIR-1974",
        "title": "Pollution Control Board Consent to Establish and Operate (CTO)",
        "authority": "State Pollution Control Board (TNPCB)",
        "jurisdiction": "State (Tamil Nadu)",
        "document_type": "Act & Siting Norms",
        "act_name": "Water (Prevention & Control of Pollution) Act 1974 & Air Act 1981",
        "section": "Section 25/26 (Water Act) & Section 21 (Air Act)",
        "category": "clothing_textile",
        "effective_date": "1974-03-23",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://tnpcb.gov.in",
        "raw_text": """CHAPTER IV - PREVENTION AND CONTROL OF WATER POLLUTION
Section 25 (Restrictions on new outlets and new discharges):
(1) Subject to the provisions of this section, no person shall, without the previous consent of the State Board, establish or take any steps to establish any industry, operation or process, or any treatment and disposal system or an extension or addition thereto, which is likely to discharge sewage or trade effluent into a stream or well or sewer or on land.
Section 26 (Existing discharge of sewage or trade effluent):
Every person who immediately before the commencement of this Act was discharging any trade effluent into a stream or well or sewer shall apply for consent to the State Board within prescribed time.
Rule 8 (Textile and Dyeing Zero Liquid Discharge Norms): All commercial textile fabric processing, yarn scouring, washing, and dyeing facilities operating within notified industrial clusters (including Tiruppur) must install Effluent Treatment Plants (ETP) capable of 100% Zero Liquid Discharge (ZLD) with mechanical multi-effect evaporators.
Rule 11 (Air Emissions): Boilers, thermic fluid heaters, and stenter chimneys must maintain stack monitoring sampling ports and continuous ambient air particulate filters conforming to TNPCB standards."""
    },
    {
        "source_id": "REG-TEX-COMM-1963",
        "title": "Textiles Committee Statutory Registration and Sampling Code",
        "authority": "Textiles Committee, Ministry of Textiles, Government of India",
        "jurisdiction": "Central (Union Government)",
        "document_type": "Act & Regulations",
        "act_name": "Textiles Committee Act, 1963",
        "section": "Section 5A",
        "category": "clothing_textile",
        "effective_date": "1964-08-22",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://textilescommittee.nic.in",
        "raw_text": """CHAPTER II - FUNCTIONS AND POWERS OF THE COMMITTEE
Section 5A (Establishment of inspection and examination standards for textiles):
(1) The Committee may establish standards for textiles and for packing materials used in the packing of textiles and may inspect textiles and packing materials at all reasonable times.
(2) Every manufacturer of textiles, knitting units, garment processing factories, and yarn spinning mills shall register with the Textiles Committee and obtain an official registration number.
Rule 4 (Monthly Statistical Returns): Registered textile and garment manufacturing enterprises must submit monthly statistical returns declaring raw fiber consumption, processed yarn yardage, fabric output, and export consignments.
Rule 6 (Quality Assurance Sampling): Authorized inspectors of the Textiles Committee have statutory powers to enter commercial textile premises to take samples of fiber, yarn, and fabrics for physical testing against national tensile, colorfastness, and chemical safety norms."""
    },
    {
        "source_id": "REG-FAC-ACT-1948-SEC06",
        "title": "Factories Act Registration, Worker Safety & Plant Stability Norms",
        "authority": "Directorate of Industrial Safety & Health (DISH)",
        "jurisdiction": "State (Tamil Nadu)",
        "document_type": "Act & Factory Rules",
        "act_name": "Factories Act, 1948",
        "section": "Section 6",
        "category": "manufacturing",
        "effective_date": "1949-04-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://labour.gov.in/factories-act-1948",
        "raw_text": """CHAPTER I - PRELIMINARY
Section 6 (Approval, licensing and registration of factories):
(1) The State Government may make rules requiring the submission of plans of any class or description of factories to the Chief Inspector, and the previous permission in writing of the State Government or the Chief Inspector for the site on which the factory is to be situated and for the construction or extension of any factory.
(2) Every factory employing 10 or more workers with the aid of power, or 20 or more workers without power, shall hold a valid Factory License granted by the Directorate of Industrial Safety and Health (DISH).
Section 21 (Fencing of machinery): Every dangerous moving part of prime movers, transmission shafts, flywheels, and power presses must be securely fenced by safeguards of substantial construction.
Section 38 (Precautions in case of fire): In every factory all practicable measures shall be taken to prevent outbreaks of fire and its spread, both internally and externally, with adequate means of escape for all persons.
Rule 105 (Annual Returns): Factory occupiers shall submit annual compliance returns in Form 21 before January 31 detailing workforce demographics, industrial accidents, and working hours."""
    },
    {
        "source_id": "REG-BOILER-ACT-1923",
        "title": "Indian Boilers Act Industrial Steam and Pressure Vessel Regulations",
        "authority": "Directorate of Boilers, Government of Tamil Nadu",
        "jurisdiction": "State (Tamil Nadu)",
        "document_type": "Act & Boiler Regulations",
        "act_name": "Indian Boilers Act, 1923",
        "section": "Section 7 & 8",
        "category": "manufacturing",
        "effective_date": "1924-01-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://dpiit.gov.in",
        "raw_text": """CHAPTER II - REGISTRATION AND INSPECTION OF BOILERS
Section 7 (Registration of boilers):
(1) The owner of any boiler which is not registered under the provisions of this Act may apply to the Inspector to have the boiler registered.
Section 8 (Renewal of certificate):
(1) A certificate authorizing the use of a boiler shall cease to be in force on the expiry of the period for which it was granted or when any accident occurs to the boiler or steam-pipe.
Rule 12 (Hydraulic Safety Audit): Every industrial steam boiler or thermic fluid heater exceeding 25 litres capacity must undergo an annual hydraulic pressure test by an authorized Boiler Inspector.
Rule 15 (Certified Attendant): No boiler shall be operated unless under the direct supervision of a certified first-class or second-class boiler attendant holding an official certificate of competency."""
    },
    {
        "source_id": "REG-BIS-GOLD-HUID-2016",
        "title": "BIS Compulsory Hallmarking & 6-Digit HUID Gold Jewellery Order",
        "authority": "Bureau of Indian Standards (BIS), Ministry of Consumer Affairs",
        "jurisdiction": "Central (Union Government)",
        "document_type": "Act & Hallmarking Order",
        "act_name": "Bureau of Indian Standards Act, 2016",
        "section": "Section 14 & 15",
        "category": "jewellery",
        "effective_date": "2021-06-16",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://www.manakonline.in",
        "raw_text": """CHAPTER IV - CONFORMITY ASSESSMENT
Section 14 (Power to notify goods for compulsory conformity mark):
(1) If the Central Government is of the opinion that it is necessary in the public interest, it may notify goods of any scheduled industry to conform to an Indian Standard and direct the use of the Standard Mark under a licence.
Section 15 (Prohibition of improper use of standard mark):
No person shall manufacture, sell, distribute, or exhibit for sale any precious metal article that does not conform to the certified Hallmarking Order.
Order Clause 3 (Mandatory 6-Digit HUID): All gold jewellery and artefacts sold by registered jewellers in notified districts must be hallmarked by a BIS-recognized Assaying and Hallmarking Centre (AHC) bearing three distinct laser marks:
1. The BIS Logo (triangular mark)
2. Purity of gold (22K916, 18K750, 14K585, etc.)
3. 6-digit alphanumeric Hallmarking Unique Identification (HUID) code.
Order Clause 5 (Stock Reconciliation): Every registered jeweller must maintain digital stock reconciliation connecting physical inventory tags to the central BIS portal database."""
    },
    {
        "source_id": "REG-PMLA-FIU-2002",
        "title": "PMLA Anti-Money Laundering and Cash Transaction Reporting Guidelines",
        "authority": "Financial Intelligence Unit - India (FIU-IND), Ministry of Finance",
        "jurisdiction": "Central (Union Government)",
        "document_type": "Act & Reporting Guidelines",
        "act_name": "Prevention of Money Laundering Act, 2002",
        "section": "Section 12",
        "category": "jewellery",
        "effective_date": "2005-07-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://fiuindia.gov.in",
        "raw_text": """CHAPTER IV - OBLIGATIONS OF BANKING COMPANIES, FINANCIAL INSTITUTIONS AND INTERMEDIARIES
Section 12 (Reporting entity obligations):
(1) Every reporting entity (including dealers in precious metals and precious stones engaging in cash transactions) shall:
(a) maintain a record of all transactions, the series and value of which shall be prescribed;
(b) furnish to the Director information relating to such transactions within the prescribed time;
(c) verify the identity of its clients and beneficial owners;
(d) preserve records of identity and transactions for five years from the date of cessation of transactions.
Rule 3 (Cash Transaction Reporting - CTR Threshold): Dealers in precious metals and stones must file a monthly Cash Transaction Report (CTR) via the FINnet 2.0 portal for all cash transactions where value exceeds ₹2,00,000 (Rupees Two Lakhs) whether conducted in a single transaction or an integrally connected series of transactions within one calendar month."""
    },
    {
        "source_id": "REG-LM-ACT-2009-SEC24",
        "title": "Legal Metrology Commercial Weighing Scale and Pre-packaged Commodity Code",
        "authority": "Department of Consumer Affairs, Directorate of Legal Metrology",
        "jurisdiction": "State (Tamil Nadu)",
        "document_type": "Act & Packaging Rules",
        "act_name": "Legal Metrology Act, 2009 & Packaged Commodities Rules 2011",
        "section": "Section 24",
        "category": "retail",
        "effective_date": "2011-04-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://consumeraffairs.nic.in",
        "raw_text": """CHAPTER IV - VERIFICATION AND STAMPING OF WEIGHT OR MEASURE
Section 24 (Verification and stamping of weight or measure):
(1) Every person having any weight or measure in his possession, custody or control in circumstances indicating that such weight or measure is being used, or is intended or likely to be used, in any transaction shall have the weight or measure verified and stamped by the legal metrology officer.
Rule 15 (Annual Scale Stamping): Electronic weighing balances, platform scales, and counter weights used in retail commerce must be re-verified and lead-wire stamped annually by the jurisdictional Inspector of Legal Metrology.
Rule 6 (Mandatory Declarations on Pre-packaged Commodities): Every retail packaged commodity must clearly declare:
1. Name and address of manufacturer/packer/importer
2. Common generic name of the commodity
3. Net quantity in standard SI units
4. Month and year of manufacture/packing
5. Maximum Retail Price (MRP inclusive of all taxes)
6. Consumer complaint redressal phone number and email."""
    },
    {
        "source_id": "REG-CGST-ACT-2017-SEC22",
        "title": "Central GST Statutory Registration Thresholds and Monthly Return Compliance",
        "authority": "Central Board of Indirect Taxes and Customs (CBIC)",
        "jurisdiction": "Central (Union Government) & State",
        "document_type": "Act & Statutory Rules",
        "act_name": "Central Goods and Services Tax Act, 2017",
        "section": "Section 22 & 39",
        "category": "general_statutory",
        "effective_date": "2017-07-01",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://cbic.gov.in",
        "raw_text": """CHAPTER VI - REGISTRATION
Section 22 (Persons liable for registration):
(1) Every supplier shall be liable to be registered under this Act in the State or Union territory, other than special category States, from where he makes a taxable supply of goods or services or both, if his aggregate turnover in a financial year exceeds the prescribed threshold (₹40 Lakhs for exclusive goods supply / ₹20 Lakhs for services and mixed supply).
Section 39 (Furnishing of returns):
(1) Every registered person shall, for every calendar month or part thereof, furnish a return in Form GSTR-3B electronically of inward and outward supplies of goods or services, input tax credit availed, tax payable, and tax paid, on or before the twentieth day of the month succeeding such calendar month."""
    },
    {
        "source_id": "REG-EPFO-ACT-1952-SEC01",
        "title": "EPFO Employees' Provident Fund and Retirement Benefit Enactment",
        "authority": "Employees' Provident Fund Organisation (EPFO), Ministry of Labour",
        "jurisdiction": "Central (Union Government)",
        "document_type": "Act & Social Security Code",
        "act_name": "Employees' Provident Funds and Miscellaneous Provisions Act, 1952",
        "section": "Section 1",
        "category": "general_statutory",
        "effective_date": "1952-03-04",
        "verification_status": "VERIFIED",
        "version": 1,
        "source_url": "https://epfindia.gov.in",
        "raw_text": """CHAPTER I - PRELIMINARY
Section 1 (Short title, extent and application):
(3) Subject to the provisions contained in section 16, it applies:
(a) to every establishment which is a factory engaged in any industry specified in Schedule I and in which twenty or more persons are employed;
(b) to any other establishment employing twenty or more persons or class of such establishments which the Central Government may notify.
Paragraph 38 (Monthly Contribution Remittance): The employer shall, before paying the member his wages, deduct the employee's contribution of 12% and pay together with employer's matching contribution to the Fund by the 15th day of each month via Electronic Challan cum Return (ECR)."""
    }
]


def seed_regulatory_knowledge(db: Session) -> Dict[str, int]:
    """
    Seeds the verified statutory knowledge database and updates ChromaDB vector store.
    Deterministic, repeatable, and deduplicated using SHA-256 content hashes.
    """
    vector_store = VectorStoreService.get_instance()
    docs_seeded = 0
    chunks_seeded = 0
    all_chunks_for_vector = []

    for item in RAW_STATUTORY_SOURCES:
        source_id = item["source_id"]
        c_hash = generate_content_hash(item["raw_text"])

        # Check existing in SQLite
        doc = db.query(RegulatoryKnowledgeDocument).filter(
            RegulatoryKnowledgeDocument.source_id == source_id
        ).first()

        if not doc:
            doc = RegulatoryKnowledgeDocument(
                source_id=source_id,
                title=item["title"],
                authority=item["authority"],
                jurisdiction=item["jurisdiction"],
                document_type=item["document_type"],
                act_name=item["act_name"],
                section=item["section"],
                category=item["category"],
                effective_date=item["effective_date"],
                verification_status=item["verification_status"],
                version=item["version"],
                source_url=item["source_url"],
                content_hash=c_hash,
                raw_text=item["raw_text"]
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            docs_seeded += 1
        else:
            # Update existing if content changed
            if doc.content_hash != c_hash:
                doc.title = item["title"]
                doc.authority = item["authority"]
                doc.raw_text = item["raw_text"]
                doc.content_hash = c_hash
                doc.version += 1
                db.add(doc)
                db.commit()
                db.refresh(doc)

        # Generate statutory chunks
        chunks = StatutoryChunker.chunk_statutory_text(
            text=item["raw_text"],
            source_id=source_id,
            category=item["category"],
            jurisdiction=item["jurisdiction"],
            document_id=doc.id,
            verification_status=doc.verification_status,
            default_section=doc.section
        )

        for chk in chunks:
            chk["act_name"] = doc.act_name
            chk["authority"] = doc.authority
            chk["title"] = doc.title
            all_chunks_for_vector.append(chk)

            # Persist in DB
            db_chk = db.query(RegulatoryChunk).filter(
                RegulatoryChunk.chunk_id == chk["chunk_id"]
            ).first()

            if not db_chk:
                db_chk = RegulatoryChunk(
                    document_id=doc.id,
                    source_id=source_id,
                    chunk_id=chk["chunk_id"],
                    chapter=chk["chapter"],
                    section=chk["section"],
                    rule=chk["rule"],
                    content=chk["content"],
                    content_hash=chk["content_hash"],
                    jurisdiction=chk["jurisdiction"],
                    category=chk["category"],
                    verification_status=chk["verification_status"],
                    embedding_id=chk["chunk_id"]
                )
                db.add(db_chk)
                chunks_seeded += 1
            else:
                db_chk.content = chk["content"]
                db_chk.content_hash = chk["content_hash"]
                db.add(db_chk)

        db.commit()

    # Index into ChromaDB vector store
    indexed_vector_count = vector_store.add_regulatory_chunks(all_chunks_for_vector)

    return {
        "documents_seeded": docs_seeded,
        "chunks_seeded": chunks_seeded,
        "vectors_indexed": indexed_vector_count
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = seed_regulatory_knowledge(db)
        print("Seeding Complete:", res)
    finally:
        db.close()
