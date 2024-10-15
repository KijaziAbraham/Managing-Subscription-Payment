document.addEventListener("DOMContentLoaded", function () {
  // Helper functions
  const select = (el, all = false) => all ? [...document.querySelectorAll(el.trim())] : document.querySelector(el.trim());
  const on = (type, el, listener, all = false) => {
    const elements = select(el, all);
    elements.forEach(e => e.addEventListener(type, listener));
  };
  const onscroll = (el, listener) => el.addEventListener('scroll', listener);

  // Form validation
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", function (event) {
      const inputs = form.querySelectorAll("input[required]");
      let valid = true;
      inputs.forEach(input => {
        if (!input.value) {
          valid = false;
          input.classList.add("invalid");
        } else {
          input.classList.remove("invalid");
        }
      });
      if (!valid) {
        event.preventDefault();
        alert("Please fill in all required fields.");
      }
    });
  });

  // Back to top button functionality
  const backToTop = select('.back-to-top');
  if (backToTop) {
    const toggleBacktotop = () => window.scrollY > 100 ? backToTop.classList.add('active') : backToTop.classList.remove('active');
    window.addEventListener('load', toggleBacktotop);
    onscroll(document, toggleBacktotop);
  }

  // Alert Timeout
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => alert.style.display = 'none', 3000);
  });

  // Navbar Links Active State on Scroll
  const navbarlinks = select('#navbar .scrollto', true);
  const navbarlinksActive = () => {
    const position = window.scrollY + 200;
    navbarlinks.forEach(navbarlink => {
      const section = select(navbarlink.hash);
      if (!section) return;
      position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)
        ? navbarlink.classList.add('active')
        : navbarlink.classList.remove('active');
    });
  };
  window.addEventListener('load', navbarlinksActive);
  onscroll(document, navbarlinksActive);

  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));


  

  // Initiate Bootstrap Validation Check
  document.querySelectorAll('.needs-validation').forEach(form => {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

  // Initiate Datatables
   select('.datatable', true).forEach(datatable => new simpleDatatables.DataTable(datatable));


  // Toggle Active/Inactive Status
  window.toggleActive = function(userId) {
    var form = document.getElementById('toggle-status-form-' + userId);
    var button = form.querySelector('button');
    var isActive = button.classList.contains('btn-toggle-active');

    // Change the button text and class based on the current state
    button.classList.toggle('btn-toggle-active', !isActive);
    button.classList.toggle('btn-toggle-inactive', isActive);
    button.textContent = isActive ? 'Inactive' : 'Active';

    // Optionally, you could submit the form here if needed
    form.submit();
  }

  // Initialize DataTables
 /* $(document).ready(function() {
    $('.datatable').DataTable({
      "pageLength": 10, // Default number of rows per page
      "lengthMenu": [5, 10, 25, 50, 100], // Options for rows per page
      "order": [[0, 'asc']], // Default sorting on the first column
      "language": {
        "search": "Search:", // Label for the search input
        "lengthMenu": "Show _MENU_ entries", // Label for the page length menu
        "info": "Showing _START_ to _END_ of _TOTAL_ entries", // Info text
        "infoEmpty": "No entries available", // Info text when there are no entries
        "infoFiltered": "(filtered from _MAX_ total entries)" // Info text for filtering
      }
    });
  });
*/


});


document.addEventListener('DOMContentLoaded', function() {
  const closeSidebarBtn = document.getElementById('close-sidebar');
  const toggleSidebarBtn = document.querySelector('.toggle-sidebar-btn');
  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('#main');
  const footer = document.querySelector('.footer');

  // Helper function to toggle sidebar visibility
  const toggleSidebar = () => {
      sidebar.classList.toggle('toggle-sidebar');
      mainContent.classList.toggle('toggle-sidebar');
      footer.classList.toggle('toggle-sidebar');
  };

  // Toggle sidebar on button click
  toggleSidebarBtn.addEventListener('click', toggleSidebar);
  closeSidebarBtn.addEventListener('click', toggleSidebar);

  // Close sidebar when clicking outside
  document.addEventListener('click', function(event) {
      if (!sidebar.contains(event.target) && !toggleSidebarBtn.contains(event.target) && sidebar.classList.contains('toggle-sidebar')) {
          toggleSidebar();
      }
  })
});


  // Update the current date in the required format
  function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const dateString = now.toLocaleDateString('en-GB', options).split(' ');
    const dayNumber = parseInt(dateString[1], 10);
    const daySuffix = ['st', 'nd', 'rd'][((dayNumber + 90) % 100 - 10) % 10 - 1] || 'th';
    const formattedDate = `${dateString[0]}&nbsp;${dayNumber}<sup>${daySuffix}</sup>&nbsp;of&nbsp;${dateString[2]},&nbsp;${dateString[3]}`;

    document.getElementById('current-date').innerHTML = formattedDate;
}
updateDate();


// Calculate end date based on date of subscription and duration
$('#id_date_of_subscription, #id_subscription_duration').change(function() {
  var subscriptionDate = $('#id_date_of_subscription').val();
  var duration = $('#id_subscription_duration').val();
  if (subscriptionDate && duration) {
      var startDate = new Date(subscriptionDate);
      startDate.setMonth(startDate.getMonth() + parseInt(duration));
      document.getElementById('end_of_subscription').value = startDate.toISOString().split('T')[0]; // Format to YYYY-MM-DD
  }
});