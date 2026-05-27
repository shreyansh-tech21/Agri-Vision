"""
Report generation service for Agri-Vision
Generates PDF reports for disease analysis and crop health
"""
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import base64


class ReportGenerator:
    """Generate PDF reports for crop analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=self.styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=20,
                spaceBefore=20
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12
            ),
            'header': ParagraphStyle(
                'CustomHeader',
                parent=self.styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#27ae60'),
                spaceAfter=10,
                spaceBefore=15
            )
        }
        return styles
    
    def generate_analysis_report(self, analysis_data, user_info):
        """Generate a comprehensive analysis report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph("Agri-Vision Crop Analysis Report", self.custom_styles['title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        metadata = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['User:', user_info.get('full_name', 'N/A')],
            ['Email:', user_info.get('email', 'N/A')],
            ['Role:', user_info.get('role', 'N/A').capitalize()]
        ]
        
        metadata_table = Table(metadata, colWidths=[1.5*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Disease Analysis Section
        disease_header = Paragraph("Disease Analysis Results", self.custom_styles['header'])
        story.append(disease_header)
        
        disease_result = analysis_data.get('disease_result', {})
        if disease_result:
            disease_data = [
                ['Predicted Disease:', disease_result.get('predicted_class', 'N/A').replace('_', ' ').title()],
                ['Confidence:', f"{disease_result.get('confidence', 0) * 100:.1f}%"],
                ['Health Score:', f"{analysis_data.get('health_score', 0):.1f}%"]
            ]
            
            disease_table = Table(disease_data, colWidths=[2*inch, 2.5*inch])
            disease_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            story.append(disease_table)
            
            # Class probabilities
            if 'class_probabilities' in disease_result:
                story.append(Spacer(1, 0.2*inch))
                prob_header = Paragraph("Class Probabilities", self.custom_styles['header'])
                story.append(prob_header)
                
                prob_data = [['Disease', 'Probability']]
                for disease, prob in disease_result['class_probabilities'].items():
                    prob_data.append([disease.replace('_', ' ').title(), f"{prob * 100:.1f}%"])
                
                prob_table = Table(prob_data, colWidths=[2.5*inch, 2*inch])
                prob_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                ]))
                story.append(prob_table)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Growth Stage Section
        growth_header = Paragraph("Growth Stage Analysis", self.custom_styles['header'])
        story.append(growth_header)
        
        growth_result = analysis_data.get('growth_result', {})
        if growth_result:
            growth_data = [
                ['Main Stage:', growth_result.get('main_class', 'N/A').replace('_', ' ').title()],
                ['Confidence:', f"{growth_result.get('confidence', 0) * 100:.1f}%"]
            ]
            
            if 'sub_classes' in growth_result:
                for sub_class, conf in growth_result['sub_classes'].items():
                    growth_data.append([sub_class.replace('_', ' ').title(), f"{conf * 100:.1f}%"])
            
            growth_table = Table(growth_data, colWidths=[2*inch, 2.5*inch])
            growth_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            story.append(growth_table)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations Section
        rec_header = Paragraph("Recommendations", self.custom_styles['header'])
        story.append(rec_header)
        
        recommendations = self._generate_recommendations(analysis_data)
        for rec in recommendations:
            rec_para = Paragraph(f"• {rec}", self.custom_styles['body'])
            story.append(rec_para)
        
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer = Paragraph(
            "Generated by Agri-Vision Cotton Analysis System",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_recommendations(self, analysis_data):
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        disease_result = analysis_data.get('disease_result', {})
        disease = disease_result.get('predicted_class', 'healthy')
        health_score = analysis_data.get('health_score', 0)
        
        if disease == 'healthy':
            recommendations.append("Plant appears healthy. Continue regular monitoring.")
            recommendations.append("Maintain current irrigation and fertilization schedule.")
        else:
            recommendations.append(f"Immediate attention required for {disease.replace('_', ' ').title()}.")
            recommendations.append("Consult with agricultural extension service for treatment options.")
            recommendations.append("Consider applying appropriate fungicides or pesticides.")
            recommendations.append("Monitor surrounding plants for signs of spread.")
        
        if health_score < 50:
            recommendations.append("Overall plant health is below optimal levels.")
            recommendations.append("Review soil nutrients and water management.")
            recommendations.append("Consider supplemental fertilization.")
        elif health_score < 70:
            recommendations.append("Plant health is moderate. Regular monitoring recommended.")
        
        growth_result = analysis_data.get('growth_result', {})
        growth_stage = growth_result.get('main_class', '')
        
        if 'boll' in growth_stage.lower():
            recommendations.append("Plant is in boll development stage - critical for yield.")
            recommendations.append("Ensure adequate water and nutrient supply.")
        elif 'flower' in growth_stage.lower():
            recommendations.append("Flowering stage - protect from pests and diseases.")
        
        return recommendations
    
    def generate_summary_report(self, analyses, user_info, date_range=None):
        """Generate a summary report for multiple analyses"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph("Agri-Vision Analysis Summary Report", self.custom_styles['title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        date_str = date_range if date_range else "All Time"
        metadata = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Date Range:', date_str],
            ['User:', user_info.get('full_name', 'N/A')],
            ['Total Analyses:', str(len(analyses))]
        ]
        
        metadata_table = Table(metadata, colWidths=[1.5*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics
        if analyses:
            healthy_count = sum(1 for a in analyses if a.get('disease_result', {}).get('predicted_class') == 'healthy')
            diseased_count = len(analyses) - healthy_count
            avg_health = sum(a.get('health_score', 0) for a in analyses) / len(analyses)
            
            stats_header = Paragraph("Overall Statistics", self.custom_styles['header'])
            story.append(stats_header)
            
            stats_data = [
                ['Total Analyses:', str(len(analyses))],
                ['Healthy Plants:', str(healthy_count)],
                ['Diseased Plants:', str(diseased_count)],
                ['Average Health Score:', f"{avg_health:.1f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[2*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Disease distribution
            disease_counts = {}
            for a in analyses:
                disease = a.get('disease_result', {}).get('predicted_class', 'unknown')
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
            
            if disease_counts:
                dist_header = Paragraph("Disease Distribution", self.custom_styles['header'])
                story.append(dist_header)
                
                dist_data = [['Disease', 'Count', 'Percentage']]
                for disease, count in disease_counts.items():
                    percentage = (count / len(analyses)) * 100
                    dist_data.append([disease.replace('_', ' ').title(), str(count), f"{percentage:.1f}%"])
                
                dist_table = Table(dist_data, colWidths=[2*inch, 1*inch, 1.5*inch])
                dist_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
                ]))
                story.append(dist_table)
        
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer = Paragraph(
            "Generated by Agri-Vision Cotton Analysis System",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
