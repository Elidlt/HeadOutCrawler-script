function generateCalendar(year, month, coloredDays) {
    const calendarContainer = document.getElementById('calendar');
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth();
    const currentDate = today.getDate();

    // Set month names
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    // Set day names
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    // Create table for the calendar
    let table = `<table class="table table-bordered"><thead><tr>`;
    days.forEach(day => {
        table += `<th>${day}</th>`;
    });
    table += `</tr></thead><tbody><tr>`;

    const firstDayOfMonth = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
        table += `<td></td>`;
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = (year === currentYear && month === currentMonth && day === currentDate);
        const isColored = coloredDays.includes(day);
        table += `<td class="${isToday ? 'today' : ''} ${isColored ? 'colored' : ''} day">${day}</td>`;

        if ((firstDayOfMonth + day) % 7 === 0) {
            table += `</tr><tr>`;
        }
    }

    // Close the table
    table += `</tr></tbody></table>`;

    // Add table to calendar container
    calendarContainer.innerHTML = table;
}

// Initialize calendar for the current month and year with example colored days


// Example function to update calendar with user input for colored days
function updateCalendar() {
    const today = new Date();
    generateCalendar(today.getFullYear(), today.getMonth(), [5, 15, 25]);
    const coloredDaysInput = document.getElementById('coloredDaysInput').value;
    const coloredDays = coloredDaysInput.split(',').map(Number);
    generateCalendar(today.getFullYear(), today.getMonth(), coloredDays);
}

// Add event listener to update button
