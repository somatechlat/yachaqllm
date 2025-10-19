# Ecuadorian Academic Source Catalog

This catalog lists the university and cultural repositories that feed the YACHAQ-LLM training corpus. Every entry has been validated as of 2025-10-18 and comes with open access terms compatible with downstream processing. For harvesting, we will proceed one source at a time using Selenium, BeautifulSoup, Scrapy, or the native OAI-PMH endpoints exposed by each DSpace instance. Processed artifacts are written to the project S3 bucket (`s3://yachaq-lex-data-bucket-<suffix>/raw/ecuador_academia/`) before downstream curation and SageMaker training.

## National Public Universities

| Institution | Repository/Library Name | URL | Content Notes |
|------------|------------------------|-----|---------------|
| Universidad Central del Ecuador (UCE) | Repositorio Digital UCE | https://www.dspace.uce.edu.ec/ | Theses, research papers, institutional academic production. DSpace platform with full-text downloads |
| Escuela Politécnica Nacional (EPN) | Repositorio Digital EPN | https://bibdigital.epn.edu.ec/ | Engineering and science theses, research projects, scientific publications |
| Escuela Superior Politécnica del Litoral (ESPOL) | DSpace ESPOL | https://www.dspace.espol.edu.ec/ | Undergraduate and graduate theses across faculties, applied sciences focus |
| ESPOL | Biblioteca Central ESPOL | https://www.cib.espol.edu.ec/ | Digital databases, subscribed scientific content, hybrid physical/digital library services |
| Universidad de Cuenca (UCUENCA) | Repositorio Digital UCUENCA | https://dspace.ucuenca.edu.ec/ | Multidisciplinary theses, dissertations, research articles |
| Universidad Técnica de Ambato (UTA) | Repositorio Digital UTA | https://repositorio.uta.edu.ec/ | Graduation projects and institutional academic output |
| Universidad Nacional de Loja (UNL) | Repositorio Digital UNL | https://dspace.unl.edu.ec/ | Agricultural and environmental research, theses, project reports |
| Universidad Técnica del Norte (UTN) | Repositorio Digital UTN | https://repositorio.utn.edu.ec/ | Theses, articles, academic publications with open access PDFs |
| Universidad Politécnica Salesiana (UPS) | Repositorio Institucional UPS | https://dspace.ups.edu.ec/ | Research output, theses, ABYA YALA publishing content |
| Universidad Católica de Santiago de Guayaquil (UCSG) | Repositorio Digital UCSG | http://repositorio.ucsg.edu.ec/ | Multidisciplinary theses, research papers, notable legal studies collection |
| Universidad Técnica de Machala (UTMACHALA) | Repositorio Digital UTMACHALA | http://repositorio.utmachala.edu.ec/ | Theses, teaching materials, research indexed by RRAAE and La Referencia |
| Universidad Técnica Particular de Loja (UTPL) | Repositorio Institucional UTPL | https://dspace.utpl.edu.ec/ | Distance education resources, learning objects, institutional production |

## Private Universities

| Institution | Repository/Library Name | URL | Content Notes |
|------------|------------------------|-----|---------------|
| Universidad San Francisco de Quito (USFQ) | Repositorio Digital USFQ | https://repositorio.usfq.edu.ec/ | Theses, dissertations, faculty research across disciplines |
| Universidad Andina Simón Bolívar (UASB) | UASB-Digital | https://repositorio.uasb.edu.ec/ | Postgraduate theses and publications in social sciences, law, Andean studies |
| UASB | Biblioteca UASB | https://biblioteca.uasb.edu.ec/ | Digital catalog with Koha, access to subscribed databases and institutional collections |
| Pontificia Universidad Católica del Ecuador (PUCE) | Repositorio Digital PUCE | https://repositorio.puce.edu.ec/ | Comprehensive academic repository for all faculties and research centers |

## Specialized Academic Institutions

| Institution | Repository/Library Name | URL | Content Notes |
|------------|------------------------|-----|---------------|
| FLACSO Ecuador | Repositorio FLACSO Andes | https://repositorio.flacsoandes.edu.ec/ | Books, working papers, journals specializing in social sciences and policy |
| FLACSO Ecuador | Biblioteca FLACSO Ecuador | https://www.flacso.edu.ec/es/biblioteca | Physical/digital library access, subscribed databases, research support |
| Instituto de Altos Estudios Nacionales (IAEN) | Repositorio IAEN | Via RRAAE | Public administration, security, international relations research |

## National Networks and Aggregators

| Institution | Platform | URL | Content Notes |
|------------|----------|-----|---------------|
| CEDIA | RRAAE | https://rraae.cedia.edu.ec/vufind/ | National OAI-PMH aggregator for open access academic content, weekly harvest cadence |
| CEDIA | REDI | https://redi.cedia.edu.ec/ | Researcher profiles, publications, collaboration graphs |
| CEDIA | ROA | https://roa.cedia.edu.ec/ | Learning object repository with open educational resources |
| CEDIA | Repositorio Multimedia | Via CEDIA platform | Audiovisual academic materials (presentations, seminars, courses) |
| Bibliotecas del Ecuador | Portal de Bibliotecas | https://www.bibliotecasdelecuador.com/ | Federated search across university library catalogs |
| COBUEC | COBUEC Network | https://www.bibliotecasdelecuador.com/cobuec/ | Consortium for inter-library resource sharing and access governance |

## Public Libraries and Cultural Institutions

| Institution | Platform | Access | Content Notes |
|------------|----------|--------|---------------|
| Banco Central del Ecuador (BCE) | Biblioteca BCE | Via COBUEC | Economic, financial, historical archives, cultural heritage |
| Casa de la Cultura Ecuatoriana (CCE) | Biblioteca CCE | Via COBUEC | Cultural heritage, arts, literature, national archives |
| Defensoría del Pueblo | Biblioteca Defensoría | Via RRAAE | Human rights, constitutional law, social justice materials |
| Biblioteca Nacional del Ecuador (BNE) | Biblioteca Nacional | Via COBUEC | National bibliography, rare books, manuscripts |

## Additional Confirmed University Repositories

| Institution | Repository/Library Name | URL | Content Notes |
|------------|------------------------|-----|---------------|
| Universidad Técnica Estatal de Quevedo (UTEQ) | Repositorio Digital UTEQ | https://repositorio.uteq.edu.ec/ | Agricultural, environmental, engineering research |
| Universidad de las Fuerzas Armadas (ESPE) | Repositorio Digital ESPE | https://repositorio.espe.edu.ec/ | Military sciences, engineering, administrative sciences |
| Universidad Regional Amazónica IKIAM | Repositorio Digital IKIAM | https://repositorio.ikiam.edu.ec/ | Biodiversity, earth sciences, Amazon-focused research |
| Universidad Estatal Amazónica (UEA) | Repositorio Digital UEA | https://repositorio.uea.edu.ec/ | Forestry, ecotourism, agricultural production |
| Universidad Laica Eloy Alfaro de Manabí (ULEAM) | Repositorio Digital ULEAM | https://repositorio.uleam.edu.ec/ | Multidisciplinary theses with coastal and marine emphasis |

## Content Types and Technical Profile

- **Document formats:** Theses (undergraduate, masters, doctoral), research articles, technical reports, books, working papers, journals, conference proceedings, learning objects.
- **Repository stack:** Predominantly DSpace with Koha catalogs. Metadata in Dublin Core or MARC21, harvested via OAI-PMH endpoints.
- **Access model:** Public/open access, Spanish-first content with growing bilingual coverage.
- **Indexing:** RRAAE, La Referencia, OpenDOAR, ROAR, Google Scholar, BASE. Persistent identifiers supplied per institution.
- **Ingestion storage:** Raw crawls land in S3 before curation and chunking for retrieval pipelines. Maintain attribution logs per batch.
- **Compliance:** Governed by COESCI, LOTAIP, and applicable Creative Commons licenses. Record license metadata for every document prior to training ingestion.

## Operating Procedure

1. Select a single source and configure a Scrapy or Selenium-based spider depending on the repository’s search UX. Prefer OAI-PMH harvesters when provided by DSpace.
2. Capture document metadata (title, authors, date, faculty, degree, URL, license) along with the PDF or supporting files.
3. Store raw payloads under `s3://yachaq-lex-data-bucket-<suffix>/raw/ecuador_academia/<institution>/YYYY/MM/DD/` with a manifest JSONL.
4. Log crawler runs and errors to `rag/ingest/logs/<institution>.log` for reproducibility.
5. After quality checks, convert documents into chunked text suitable for retrieval and push curated artifacts to the training lake for SageMaker ingestion.
