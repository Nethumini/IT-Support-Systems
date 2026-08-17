import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

class PDFService {
  /**
   * Generate a professional PDF report
   * @param {HTMLElement} element - The element to convert to PDF
   * @param {Object} options - Configuration options
   * @returns {Promise<void>}
   */
  async generateReport(element, options = {}) {
    const {
      title = 'Report',
      subtitle = 'IT Support Systems System Report',
      reportType = 'General',
      dateRange = 'Last 7 Days',
      filename = 'report.pdf'
    } = options

    try {
      // Create PDF document
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      })

      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const margin = 15
      const contentWidth = pageWidth - margin * 2

      let currentY = margin

      // Set light background
      pdf.setFillColor(248, 248, 248)
      pdf.rect(0, 0, pageWidth, pageHeight, 'F')

      // Add Header
      this.addHeader(pdf, title, subtitle, reportType, dateRange, pageWidth, margin)
      currentY = 50

      // Convert element to canvas
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        windowHeight: element.scrollHeight
      })

      const imgWidth = contentWidth
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      const imgData = canvas.toDataURL('image/png')

      // Add content with pagination
      let heightLeft = imgHeight
      let position = currentY
      let pageNum = 1

      while (heightLeft > 0) {
        if (position + 40 > pageHeight - margin) {
          // Add footer to current page
          this.addFooter(pdf, pageNum, pageWidth, pageHeight, margin)
          
          // Add new page
          pdf.addPage()
          pageNum++
          
          // Add light background to new page
          pdf.setFillColor(248, 248, 248)
          pdf.rect(0, 0, pageWidth, pageHeight, 'F')
          
          // Add header to new page
          this.addHeader(pdf, title, subtitle, reportType, dateRange, pageWidth, margin)
          position = 50
        }

        const availableHeight = pageHeight - margin - position - 15 // Leave space for footer

        if (heightLeft > availableHeight) {
          pdf.addImage(imgData, 'PNG', margin, position, imgWidth, availableHeight)
          heightLeft -= availableHeight
          position = pageHeight - margin - 15
        } else {
          pdf.addImage(imgData, 'PNG', margin, position, imgWidth, heightLeft)
          heightLeft = 0
        }
      }

      // Add footer to last page
      this.addFooter(pdf, pageNum, pageWidth, pageHeight, margin)

      // Download PDF
      pdf.save(filename)
    } catch (err) {
      console.error('Error generating PDF:', err)
      throw new Error('Failed to generate PDF: ' + err.message)
    }
  }

  /**
   * Add header to PDF page
   */
  addHeader(pdf, title, subtitle, reportType, dateRange, pageWidth, margin) {
    const headerY = 10

    // Company/App name
    pdf.setFontSize(10)
    pdf.setTextColor(100, 100, 100)
    pdf.text('IT Support Systems', margin, headerY)

    // Report title
    pdf.setFontSize(16)
    pdf.setTextColor(30, 30, 30)
    pdf.setFont(undefined, 'bold')
    pdf.text(title, margin, headerY + 12)

    // Subtitle and metadata
    pdf.setFontSize(9)
    pdf.setTextColor(120, 120, 120)
    pdf.setFont(undefined, 'normal')
    pdf.text(`${subtitle}`, margin, headerY + 19)
    pdf.text(`Report Type: ${reportType} | Period: ${dateRange}`, margin, headerY + 24)

    // Divider line
    pdf.setDrawColor(200, 200, 200)
    pdf.line(margin, headerY + 28, pageWidth - margin, headerY + 28)
  }

  /**
   * Add footer to PDF page
   */
  addFooter(pdf, pageNum, pageWidth, pageHeight, margin) {
    const footerY = pageHeight - 10

    // Divider line
    pdf.setDrawColor(200, 200, 200)
    pdf.line(margin, footerY - 5, pageWidth - margin, footerY - 5)

    // Footer text
    pdf.setFontSize(8)
    pdf.setTextColor(150, 150, 150)
    pdf.setFont(undefined, 'normal')

    // Generated date
    const now = new Date()
    const dateStr = now.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
    pdf.text(`Generated: ${dateStr}`, margin, footerY)

    // Page number (right aligned)
    pdf.text(`Page ${pageNum}`, pageWidth - margin - 15, footerY)

    // Company info
    pdf.setTextColor(180, 180, 180)
    pdf.text('© 2025 IT Support Systems System. Confidential.', pageWidth / 2, footerY, {
      align: 'center'
    })
  }

  /**
   * Generate filename with timestamp
   */
  generateFilename(reportType, dateRange) {
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]
    const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-')
    const typeStr = reportType.toLowerCase().replace(/\s+/g, '-')
    return `report-${typeStr}-${dateStr}-${timeStr}.pdf`
  }
}

export const pdfService = new PDFService()
