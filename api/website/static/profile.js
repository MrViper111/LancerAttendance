userData = null;

async function fetchUser(name) {
    try {
        const response = await fetch('/api/get_user?name=' + name.replace("_", " "));
        if (!response.ok) throw new Error('Failed to fetch user');

        const jsonData = await response.json();
        userData = jsonData.response;

        main();

    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

// ---------- Step 1: Update user profile info ----------
function updateUserProfile(user) {
  // We assume the second ".container1.inline-container" in your HTML
  // is the one containing Name, Email, Position, and Score:
  //
  // <div class="container1 inline-container">
  //   <div>
  //     <p class="lesser">Name</p>
  //     <p>David Sachmanyan</p>
  //   </div>
  //   <div>
  //     <p class="lesser">Email</p>
  //     <p>dsachmanyan25@lasallehs.org</p>
  //   </div>
  //   <div>
  //     <p class="lesser">Position</p>
  //     <p>Chairman</p>
  //   </div>
  //   <div>
  //     <p class="lesser">Score</p>
  //     <p>942</p>
  //   </div>
  // </div>
  //
  // We'll replace the textContent in those <p> elements with userData.

  var containers = document.getElementsByClassName("container1");
  // The second container with inline-container is index 1 if your HTML structure hasn't changed
  var profileContainer = document.getElementsByClassName("inline-container")[1];

  // Each child <div> has 2 <p> tags: the second <p> is the actual data.
  // 0 => Name, 1 => Email, 2 => Position, 3 => Score.
  profileContainer.children[0].getElementsByTagName("p")[1].textContent = user.name;
  profileContainer.children[1].getElementsByTagName("p")[1].textContent = user.email;
  profileContainer.children[2].getElementsByTagName("p")[1].textContent = user.position;
  profileContainer.children[3].getElementsByTagName("p")[1].textContent = user.score;
}

// ---------- Step 2: Helper functions for attendance ----------

// Converts a Unix timestamp (in seconds) to a "H:MM" string.
function formatTime(timestamp) {
  var date = new Date(timestamp * 1000);
  var hours = date.getHours();
  var minutes = date.getMinutes();
  return hours + ":" + (minutes < 10 ? "0" + minutes : minutes);
}

// Converts a duration (in seconds) to a "hh:mm" string.
function formatDuration(seconds) {
  var hrs = Math.floor(seconds / 3600);
  var mins = Math.floor((seconds % 3600) / 60);
  var hStr = hrs < 10 ? "0" + hrs : hrs;
  var mStr = mins < 10 ? "0" + mins : mins;
  return hStr + ":" + mStr;
}

// Returns today's date as "MM/DD/YY".
function getCurrentDateFormatted() {
  var date = new Date();
  var m = date.getMonth() + 1;
  var d = date.getDate();
  var y = date.getFullYear() % 100;

  if (m < 10) m = "0" + m;
  if (d < 10) d = "0" + d;
  if (y < 10) y = "0" + y;

  return m + "/" + d + "/" + y;
}

// Groups attendance records by date (e.g., "03/04/25" => [records...]).
function groupAttendance(attendanceArray) {
  var groups = {};
  attendanceArray.forEach(function(record) {
    if (!groups[record.date]) {
      groups[record.date] = [];
    }
    groups[record.date].push(record);
  });
  return groups;
}

// Returns all records in 'attendance' whose date matches 'date'.
function getRecordsForDate(date, attendance) {
  return attendance.filter(function(record) {
    return record.date === date;
  });
}

// Creates one "card" (<div class="container1 inline-container">) for a given date and records.
function createCardForDate(date, records) {
  var currentDate = getCurrentDateFormatted();
  var cardDiv = document.createElement("div");
  cardDiv.className = "container1 inline-container";

  // Calculate total time present.
  var totalSeconds = 0;
  records.forEach(function(record) {
    if (record.out !== null) {
      totalSeconds += (record.out - record.in);
    } else if (date === currentDate) {
      // No 'out' but it's today => treat as present until now
      var nowInSeconds = Math.floor(Date.now() / 1000);
      totalSeconds += (nowInSeconds - record.in);
    }
  });

  // Build the check-in history. If no records, we'll have no spans.
  var historySpans = "";
  records.forEach(function(record) {
    var inTime = formatTime(record.in);
    var outTime = record.out ? formatTime(record.out) : "Present";
    historySpans += '<span class="check-in-out">' + inTime +
                    ' <span class="lesser">-</span> ' + outTime + '</span>';
  });

  // If there's no attendance data for the day, we at least show an empty set of spans.
  // For today's card, we use a specific layout:
  if (date === currentDate) {
    cardDiv.innerHTML = ''
      + '<div>'
      +   '<p class="lesser">Date</p>'
      +   '<p>' + date + '</p>'
      + '</div>'
      + '<div>'
      +   '<p class="lesser">Currently Present</p>'
      +   '<p>' + formatDuration(totalSeconds) + '</p>'
      + '</div>'
      + '<div>'
      +   '<span class="lesser">Today\'s Check-in History</span>'
      +   historySpans
      + '</div>';
  } else {
    // Past date layout:
    cardDiv.innerHTML = ''
      + '<div>'
      +   '<span class="lesser">Date: </span> <span>' + date + '</span>'
      + '</div>'
      + '<div>'
      +   '<span class="lesser">Time Present: </span> <span>' + formatDuration(totalSeconds) + '</span>'
      + '</div>'
      + '<div>'
      +   '<span class="lesser">History</span>'
      +   historySpans
      + '</div>';
  }
  return cardDiv;
}

// ---------- Step 3: Render the attendance cards. ----------
// ALWAYS create a card for the current date, then create cards for any past dates that exist.
function renderUsers(user) {
  var container = document.getElementById("attendanceCards");
  if (!container) {
    console.error("Element with id='attendanceCards' not found in the DOM.");
    return;
  }

  container.innerHTML = "";
  var currentDate = getCurrentDateFormatted();

  // First, create the card for today's date (always).
  var recordsForToday = getRecordsForDate(currentDate, user.attendance);
  var todayCard = createCardForDate(currentDate, recordsForToday);
  container.appendChild(todayCard);

  // Next, group the attendance by date, and add cards for past dates (i.e. date !== currentDate).
  var groups = groupAttendance(user.attendance);
  for (var date in groups) {
    if (groups.hasOwnProperty(date) && date !== currentDate) {
      var card = createCardForDate(date, groups[date]);
      container.appendChild(card);
    }
  }
}

function downloadJSON(jsonData) {
    if (!jsonData) {
        console.error('Invalid JSON data');
        return;
    }

    const jsonString = JSON.stringify(jsonData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = jsonData.name.replace(" ", "");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
}




// ---------- Step 4: Main entry point ----------
function main() {
  // Update the displayed name, email, position, and score
  updateUserProfile(userData);
  // Create the current day card + any past day cards
  renderUsers(userData);
}

// ---------- Step 5: Wait until the DOM is ready, then run main ----------