from pypdf import PdfReader, PdfWriter
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_pdf(input_path: str):
    """
    将PDF文件按照不同页数分割并保存到相应目录
    """
    try:
        # 读取PDF文件
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        # 获取基础文件名（不含扩展名）
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        # 创建主输出目录
        output_base_dir = os.path.join(os.path.dirname(input_path), base_name)
        
        # 定义分割方案
        split_schemes = {
            'one_page': 1,
            '5_page': 5,
            '10_page': 10,
            '20_page': 20
        }
        
        # 为每种分割方案创建目录并分割PDF
        for scheme_name, page_count in split_schemes.items():
            # 创建子目录
            scheme_dir = os.path.join(output_base_dir, scheme_name)
            os.makedirs(scheme_dir, exist_ok=True)
            
            # 计算需要生成多少个文件
            num_files = (total_pages + page_count - 1) // page_count
            
            # 分割并保存PDF
            for i in range(num_files):
                writer = PdfWriter()
                start_page = i * page_count
                end_page = min(start_page + page_count, total_pages)
                
                # 添加页面到新PDF
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                # 保存分割后的PDF
                output_path = os.path.join(
                    scheme_dir, 
                    f"{base_name}_{i+1:03d}.pdf"
                )
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                logger.info(f"Created {output_path} ({end_page-start_page} pages)")
        
        logger.info(f"PDF splitting completed. Output directory: {output_base_dir}")
        return output_base_dir
        
    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        raise

if __name__ == "__main__":
    # 示例用法
    pdf_path = "data/Boeing-Sustainability-Report.pdf"  # 替换为实际的PDF路径
    split_pdf(pdf_path)
