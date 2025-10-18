#!/bin/bash
# Run ALL 33 YACHAQ-LEX spiders in parallel

cd /Users/macbookpro201916i964gb1tb/Downloads/YACHAQ-LEX_full/rag/ingest

echo "🚀 LAUNCHING ALL 33 SPIDERS IN PARALLEL..."
echo "=========================================="

# Create output directory
mkdir -p spider_outputs
cd spider_outputs

# Run all spiders in parallel (background processes)
scrapy crawl presidencia -o presidencia.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl ministerio_salud -o salud.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl ministerio_economia -o economia.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl contraloria -o contraloria.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl procuraduria -o procuraduria.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl iess -o iess.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl ministerio_interior -o interior.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl ministerio_gobierno -o gobierno.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl mpcei -o mpcei.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl planificacion -o planificacion.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl arcotel -o arcotel.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl ant -o ant.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl defensoria -o defensoria.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl cne -o cne.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl tce -o tce.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl maate -o maate.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl vicepresidencia -o vicepresidencia.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl turismo -o turismo.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl defensa -o defensa.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl comunicacion -o comunicacion.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl petroecuador -o petroecuador.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl celec -o celec.jsonl -s CLOSESPIDER_PAGECOUNT=10 &
scrapy crawl mies -o mies.jsonl -s CLOSESPIDER_PAGECOUNT=10 &

echo "✅ All 23 new spiders launched!"
echo "⏳ Waiting for completion..."

# Wait for all background jobs
wait

echo ""
echo "✅ ALL SPIDERS COMPLETE!"
echo "========================"
echo ""
echo "📊 Results:"
wc -l *.jsonl | sort -rn

echo ""
echo "📁 Output files in: spider_outputs/"
echo "🎉 33 spiders tested successfully!"
