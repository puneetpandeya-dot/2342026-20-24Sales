document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const filenameDisplay = document.getElementById('filename');
    const processBtn = document.getElementById('process-btn');
    const loader = document.getElementById('loader');
    const results = document.getElementById('results');

    let selectedFile = null;

    // Drag and Drop
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary-color)';
        dropZone.style.background = 'rgba(30, 41, 59, 0.9)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-color)';
        dropZone.style.background = 'var(--card-bg)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-color)';
        dropZone.style.background = 'var(--card-bg)';
        
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (file.name.endsWith('.csv')) {
            selectedFile = file;
            filenameDisplay.textContent = `Selected: ${file.name}`;
            fileInfo.classList.remove('hidden');
            results.classList.add('hidden');
        } else {
            alert('Please upload a CSV file.');
        }
    }

    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);

        fileInfo.classList.add('hidden');
        loader.classList.remove('hidden');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                alert('Error: ' + data.error);
                loader.classList.add('hidden');
                fileInfo.classList.remove('hidden');
                return;
            }

            renderResults(data);
        } catch (error) {
            console.error('Upload failed:', error);
            alert('An error occurred while processing the file.');
        } finally {
            loader.classList.add('hidden');
        }
    });

    function renderResults(data) {
        // Summary
        document.getElementById('total-revenue').textContent = formatCurrency(data.summary.total_revenue);
        document.getElementById('total-orders').textContent = data.summary.total_orders.toLocaleString();
        document.getElementById('total-customers').textContent = data.summary.total_customers.toLocaleString();
        document.getElementById('top-product').textContent = data.summary.top_product;

        // Highlights
        const highlightsList = document.getElementById('highlights-list');
        highlightsList.innerHTML = '';
        data.highlights.forEach(highlight => {
            const li = document.createElement('li');
            li.textContent = highlight;
            highlightsList.appendChild(li);
        });

        // Weekly Table
        const tbody = document.querySelector('#report-table tbody');
        tbody.innerHTML = '';
        data.weekly_report.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.WeekStr}</td>
                <td>${formatCurrency(row.Revenue)}</td>
                <td>${row.InvoiceNo.toLocaleString()}</td>
                <td>${row.CustomerID.toLocaleString()}</td>
                <td>${row.Quantity.toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        });

        results.classList.remove('hidden');
        results.style.animation = 'fadeIn 0.6s ease-out forwards';
        
        // Scroll to results
        results.scrollIntoView({ behavior: 'smooth' });
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: 'GBP'
        }).format(value);
    }
});
