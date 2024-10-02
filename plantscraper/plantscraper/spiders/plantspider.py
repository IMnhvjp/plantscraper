import scrapy
import parsel
import re


class PlantspiderSpider(scrapy.Spider):
    name = "plantspider"
    allowed_domains = ["botanyvn.com"]
    start_urls = ["https://www.botanyvn.com/cnt.asp?param=edir&list=species"]

    def parse(self, response):
        plants = response.css('ol li')
        for plant in plants:
            relative_url = plant.css('a').attrib['href'].strip()
            plant_url = 'https://www.botanyvn.com/' + relative_url
            yield response.follow(plant_url, callback = self.parse_plant_page)

        next_page = response.css('div#divPresent table:nth-of-type(2) tr td:nth-of-type(3) a::attr(href)').get().strip()
        
        if next_page is not None:
            next_page_url = 'https://www.botanyvn.com/' + next_page

            yield response.follow(next_page_url, callback = self.parse)


    def parse_plant_page(self, response):
        name_infor = response.css('div#divPresent fieldset p b')
        classifications = response.css('table#tblContent tr:nth-of-type(2) td:nth-of-type(3) table tr:nth-of-type(2) td:nth-of-type(2) table tr td a')
        descriptions = response.css('div#divPresent fieldset:nth-of-type(2) p::text').getall()

        if len(name_infor) > 3 and len(classifications) > 5:
            scientific_name = name_infor[0].css('i::text').get()
            english_name = name_infor[1].css('i::text').get()

            vietnamese_name = name_infor[2].css('::text').get()
            array_vietnamese_name = [name.strip() for name in re.split('[,;]', vietnamese_name) if name.strip()]
            
            selector = parsel.Selector(text=name_infor[3].get())
            name_lists = selector.xpath('string()').get()
            other_names = [name.strip() for name in re.split('[,;]', name_lists) if name.strip()]

            description = '\n'.join(descriptions)

            division = classifications[1].css('::text').get().strip()
            division_description = classifications[1].css('::attr(title)').get().strip()

            _class = classifications[2].css('::text').get().strip()
            _class_description = classifications[2].css('::attr(title)').get().strip()

            order = classifications[3].css('::text').get().strip()
            order_description = classifications[3].css('::attr(title)').get().strip()

            familia = classifications[4].css('::text').get().strip()
            familia_description = classifications[4].css('::attr(title)').get().strip()

            genus = classifications[5].css('::text').get().strip()
            genus_description = classifications[5].css('::attr(title)').get().strip()

            yield {
                'url': response.url,
                'scientific_name': scientific_name,
                'english_name': english_name,
                'vietnamese_name': array_vietnamese_name,
                'other_names': other_names,
                'division': division,
                'division_description': division_description,
                '_class': _class,
                '_class_description': _class_description,
                'order': order,
                'order_description': order_description,
                'family': familia,
                'family_description': familia_description,
                'genus': genus,
                'genus_description': genus_description,
                'description': description
            }