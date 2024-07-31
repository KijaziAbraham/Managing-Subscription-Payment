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

 
  // Handle Collapse and Expand of Sidebar Menu Items
  const handleSidebarNavCollapse = (e) => {
    e.preventDefault();
    const target = select(e.target.getAttribute('href'));
    if (target) {
      target.classList.toggle('collapse');
      e.target.classList.toggle('collapsed');
    }
  };
  on('click', '.sidebar-nav .nav-link[data-toggle="collapse"]', handleSidebarNavCollapse, true);
  select('.sidebar-nav .nav-link[data-toggle="collapse"]', true).forEach(navLink => {
    const target = select(navLink.getAttribute('href'));
    if (target && !navLink.classList.contains('collapsed')) target.classList.add('collapse');
  });

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
  // select('.datatable', true).forEach(datatable => new simpleDatatables.DataTable(datatable));

 
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
  $(document).ready(function() {
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

  // Sidebar Toggle and Menu Item Collapse/Expand
  document.addEventListener('DOMContentLoaded', function() {
    const toggleSidebarBtn = document.querySelector('.toggle-sidebar-btn');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('#main');
    const footer = document.querySelector('#footer');

    toggleSidebarBtn.addEventListener('click', function() {
      sidebar.classList.toggle('toggle-sidebar');
      mainContent.classList.toggle('toggle-sidebar');
      footer.classList.toggle('toggle-sidebar');
    });

    document.querySelectorAll('.nav-link[data-bs-toggle="collapse"]').forEach(function(element) {
      element.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('data-bs-target'));
        const icon = this.querySelector('.fa-chevron-left');

        if (target.classList.contains('show')) {
          icon.style.transform = 'rotate(0deg)';
        } else {
          icon.style.transform = 'rotate(-90deg)';
        }

        target.classList.toggle('show');
      });
    });
  });
});

$(document).ready(function() {
  // Show notification dropdown and hide message dropdown
  $('#notifications-toggle').on('click', function(event) {
      event.preventDefault();
      $('#messages-menu').removeClass('show'); // Hide message dropdown
      $('#notifications-menu').toggleClass('show'); // Toggle notification dropdown
  });

  // Show message dropdown and hide notification dropdown
  $('#messages-toggle').on('click', function(event) {
      event.preventDefault();
      $('#notifications-menu').removeClass('show'); // Hide notification dropdown
      $('#messages-menu').toggleClass('show'); // Toggle message dropdown
  });

  // Hide dropdowns when clicking outside
  $(document).click(function(event) {
      if (!$(event.target).closest('.nav-link, .dropdown-menu').length) {
          $('.dropdown-menu').removeClass('show'); // Hide all dropdowns
      }
  });
});


