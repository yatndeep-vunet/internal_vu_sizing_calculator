document.addEventListener('DOMContentLoaded', function() {
     // Tab functionality
  const k8s_tab = document.getElementById('k8s_tab');
  const vms_tab = document.getElementById('vms_tab');
  const k8s_table = document.getElementById('k8s_table');
  const vms_table = document.getElementById('vms_table');

  // Function to switch tabs
  function activateTab(tab, contentToShow, contentToHide) {
      // Reset all tabs
      k8s_tab.classList.remove('bg-blue-600');
      vms_tab.classList.remove('bg-blue-600');
      // Highlight active tab
      tab.classList.add('bg-blue-600');

      // Show and hide tables
      contentToShow.classList.remove('hidden');
      contentToHide.classList.add('hidden');
  }

  // Event listeners for tabs
  k8s_tab.addEventListener('click', () => activateTab(k8s_tab, k8s_table, vms_table));
  vms_tab.addEventListener('click', () => activateTab(vms_tab, vms_table, k8s_table));

  alert("Tab.js loaded");
});