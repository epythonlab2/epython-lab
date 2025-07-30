// profilePanel.js

// --- Cached DOM elements ---
const profileBtn = document.getElementById("profileButton");
const sideNav = document.getElementById("profileSideNav");
const backdrop = document.getElementById("profileBackdrop");
const closeBtn = document.getElementById("closeProfileSideNav");

const editProfileModal = document.getElementById("editProfileModal");
const editProfileModalBackdrop = document.getElementById("editProfileModalBackdrop");
const cancelEditProfileBtn = document.getElementById("cancelEditProfile");
const editProfileForm = document.getElementById("editProfileForm");

const closeEditProfileModalBtn = editProfileModal.querySelector('button[aria-label="Close profile panel"]');
const focusableSelectors = 'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])';

// --- Focus Trap Utility ---
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(focusableSelectors);
  if (focusableElements.length === 0) return () => {};

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  function handleKeyDown(event) {
    if (event.key === "Tab") {
      if (event.shiftKey) {
        if (document.activeElement === firstFocusable) {
          event.preventDefault();
          lastFocusable.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          event.preventDefault();
          firstFocusable.focus();
        }
      }
    }
  }

  element.addEventListener("keydown", handleKeyDown);

  return () => element.removeEventListener("keydown", handleKeyDown);
}

// --- Side Navigation Panel ---
let lastFocusedElementSideNav = null;
let releaseFocusTrapSideNav = null;

function openSideNav() {
  lastFocusedElementSideNav = document.activeElement;
  sideNav.classList.remove("translate-x-full", "opacity-0", "invisible", "pointer-events-none");
  backdrop.classList.remove("opacity-0", "invisible", "pointer-events-none");
  profileBtn.setAttribute("aria-expanded", "true");
  sideNav.focus();
  releaseFocusTrapSideNav = trapFocus(sideNav);
}

function closeSideNav() {
  sideNav.classList.add("translate-x-full", "opacity-0", "invisible", "pointer-events-none");
  backdrop.classList.add("opacity-0", "invisible", "pointer-events-none");
  profileBtn.setAttribute("aria-expanded", "false");
  lastFocusedElementSideNav?.focus();
  releaseFocusTrapSideNav?.();
}

// Toggle side nav on profile button click
profileBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  if (sideNav.classList.contains("translate-x-full")) {
    openSideNav();
  } else {
    closeSideNav();
  }
});

// Close side nav handlers
closeBtn.addEventListener("click", closeSideNav);
backdrop.addEventListener("click", closeSideNav);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !sideNav.classList.contains("translate-x-full")) {
    closeSideNav();
  }
});

// --- Edit Profile Modal ---
let lastFocusedElementModal = null;
let releaseFocusTrapModal = null;

function openProfileModal() {
  lastFocusedElementModal = document.activeElement;
  editProfileModal.classList.remove("opacity-0", "invisible", "pointer-events-none");
  editProfileModalBackdrop.classList.remove("opacity-0", "invisible", "pointer-events-none");
  releaseFocusTrapModal = trapFocus(editProfileModal);
  const firstInput = editProfileModal.querySelector("input, button, select, textarea");
  firstInput?.focus();
}

function closeProfileModal() {
  editProfileModal.classList.add("opacity-0", "invisible", "pointer-events-none");
  editProfileModalBackdrop.classList.add("opacity-0", "invisible", "pointer-events-none");
  lastFocusedElementModal?.focus();
  releaseFocusTrapModal?.();
}

// Close modal event listeners
if (closeEditProfileModalBtn) closeEditProfileModalBtn.addEventListener("click", closeProfileModal);
cancelEditProfileBtn.addEventListener("click", closeProfileModal);
editProfileModalBackdrop.addEventListener("click", (e) => {
  if (e.target === editProfileModalBackdrop) closeProfileModal();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !editProfileModal.classList.contains("opacity-0")) {
    closeProfileModal();
  }
});

// --- Navigation Actions Handler ---
function handleNavClick(action) {
  action();
  closeSideNav();
}

// --- Logout Function (placeholder) ---
// function logoutUser() {
//   console.log("Logout triggered");
//   // TODO: Implement actual logout logic here
// }

// --- Edit Profile Form Handling ---
editProfileForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const password = editProfileForm.profilePassword.value;
  const confirmPassword = editProfileForm.confirmPassword.value;

  if (password && password !== confirmPassword) {
    alert("Passwords do not match.");
    return;
  }

  const formData = {
    name: editProfileForm.profileFullName.value,
    email: editProfileForm.profileEmail.value,
    password: password,
    // avatar: editProfileForm.profileAvatar.value, // Uncomment if used
  };

  const saveBtn = document.getElementById("saveProfileBtn");
  const originalText = saveBtn.textContent;
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";

  try {
    // TODO: Replace this with your actual API call
    console.log("Saving profile data:", formData);
    await new Promise((resolve) => setTimeout(resolve, 1500)); // Simulate request delay

    closeProfileModal();
  } catch (error) {
    alert("Failed to save profile.");
    console.error(error);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = originalText;
  }
});

// --- Enable Save Button Only When Form Changes ---
(() => {
  const form = editProfileForm;
  const saveBtn = form.querySelector('button[type="submit"]');
  if (!saveBtn) return;

  // Capture initial input values
  const initialValues = {};
  for (const input of form.elements) {
    if (input.tagName === "INPUT") {
      initialValues[input.id] = input.value;
    }
  }

  // Check if any input changed from initial value
  const hasChanges = () => {
    for (const input of form.elements) {
      if (input.tagName === "INPUT" && input.value !== initialValues[input.id]) {
        return true;
      }
    }
    return false;
  };

  // Toggle save button disabled state on input change
  form.addEventListener("input", () => {
    saveBtn.disabled = !hasChanges();
  });

  // Initially disable the button
  saveBtn.disabled = true;
})();

// --- Expose functions for inline usage ---
window.handleNavClick = handleNavClick;
window.openProfileModal = openProfileModal;
// window.logoutUser = logoutUser;
