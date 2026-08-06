document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(function (form) {
        form.setAttribute('autocomplete', 'off');
    });

    document.querySelectorAll('input, select, textarea').forEach(function (field) {
        if (field.type === 'password') {
            field.setAttribute('autocomplete', 'new-password');
        } else {
            field.setAttribute('autocomplete', 'off');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    var err = params.get('form_error');
    if (err) {
        sessionStorage.removeItem('pendingToast');

        showToast(err, 'error');
        params.delete('form_error');
        var qs = params.toString();
        var newUrl = window.location.pathname + (qs ? '?' + qs : '');
        window.history.replaceState({}, '', newUrl);
    }
});

/* ---- Debounce helper ---- */
function debounce(fn, delay) {
    var timer = null;
    return function () {
        var args = arguments;
        var ctx = this;
        clearTimeout(timer);
        timer = setTimeout(function () { fn.apply(ctx, args); }, delay);
    };
}

function showToast(message, type) {
    type = type || 'success';

    var container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(function () {
        toast.classList.add('show');
    });

    setTimeout(function () {
        toast.classList.remove('show');
        setTimeout(function () { toast.remove(); }, 250);
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    var menu = document.getElementById('profileMenu');
    var link = document.getElementById('changePasswordMenuLink');
    if (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            if (menu) menu.classList.remove('open');
            openModal('changePasswordModal');
        });
    }
});

function toggleProfileMenu() {
    var menu = document.getElementById('profileMenu');
    if (menu) menu.classList.toggle('open');
}

function closeProfileMenu() {
    var menu = document.getElementById('profileMenu');
    if (menu) menu.classList.remove('open');
}

document.addEventListener('click', function (e) {
    var menu = document.getElementById('profileMenu');
    var btn = document.getElementById('profileBtn');

    if (menu && btn && !btn.contains(e.target) && !menu.contains(e.target)) {
        closeProfileMenu();
    }
});

function openEditModal(btn, modalId, formId, baseUrl) {
    var form = document.getElementById(formId);
    if (!form) return;

    // Gather everything first (reads), then apply all writes together in one frame
    // instead of interleaving querySelector reads with value writes per key.
    var action = baseUrl + '/' + btn.dataset.id + '/edit';
    var fieldWrites = [];
    Object.keys(btn.dataset).forEach(function (key) {
        if (key === 'id') return;
        var field = form.querySelector('[name="' + key + '"]');
        if (field) fieldWrites.push({ field: field, value: btn.dataset[key] });
    });

    requestAnimationFrame(function () {
        form.action = action;
        fieldWrites.forEach(function (item) {
            item.field.value = item.value;
        });
        clearFormErrors(form);
        openModal(modalId);
    });
}

function openModal(id) {
    var modal = document.getElementById(id);
    if (!modal) return;
    clearFormErrors(modal);
    modal.classList.add('active');
    document.body.classList.add('scroll-locked');
}

function closeModal(id) {
    var modal = document.getElementById(id);
    if (!modal) return;
    clearFormErrors(modal);
    modal.classList.remove('active');
    if (!document.querySelector('.modal-bg.active')) {
        document.body.classList.remove('scroll-locked');
    }
}

/* ---- Manage access ---- */
function navigateAdminFilter(select) {
    var value = select.value;
    window.location.href = '/admin/permissions' + (value ? '?admin_id=' + value : '');
}

function postTo(action, fields) {
    var form = document.createElement('form');
    form.method = 'post';
    form.action = action;
    form.style.display = 'none';

    (fields || []).forEach(function (f) {
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = f.name;
        input.value = f.value;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.save-perm-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.user-access-card');
            var userId = card.getAttribute('data-user-id');

            var fields = [];
            card.querySelectorAll('.perm-checkbox:checked').forEach(function (cb) {
                fields.push({ name: 'modules', value: cb.value });
            });

            if (btn.disabled) return;
            btn.classList.add('btn-loading');
            btn.disabled = true;

            postTo('/admin/permissions/' + userId, fields);
        });
    });

    document.querySelectorAll('.delete-user-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.user-access-card');
            var userId = card.getAttribute('data-user-id');
            var username = card.getAttribute('data-username');

            if (!confirm('Delete ' + username + '? This removes their login and all granted access permanently.')) {
                return;
            }

            if (btn.disabled) return;
            btn.classList.add('btn-loading');
            btn.disabled = true;

            postTo('/admin/users/' + userId + '/delete', []);
        });
    });

    document.querySelectorAll('.reset-pwd-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.user-access-card');
            var userId = card.getAttribute('data-user-id');
            var username = card.getAttribute('data-username');
            document.getElementById('resetPasswordForm').action = '/admin/permissions/' + userId + '/reset-password';
            document.getElementById('resetPasswordUsername').textContent = username;
            document.getElementById('resetPasswordInput').value = '';
            openModal('resetPasswordModal');
        });
    });
});

/* ---- Sidebar nav groups ---- */
function closeAllGroups() {
    document.querySelectorAll('.nav-submenu').forEach(function (menu) {
        menu.classList.remove('open');
    });

    document.querySelectorAll('.nav-group-toggle').forEach(function (btn) {
        btn.classList.remove('open');
    });
}

function openGroup(id) {
    closeAllGroups();

    var submenu = document.getElementById(id + "-submenu");
    var toggle = document.getElementById(id + "-toggle");

    if (submenu) submenu.classList.add("open");
    if (toggle) toggle.classList.add("open");
}

function closeGroup(id) {
    var submenu = document.getElementById(id + "-submenu");
    var toggle = document.getElementById(id + "-toggle");

    if (submenu) submenu.classList.remove("open");
    if (toggle) toggle.classList.remove("open");
}

/* ---- Mobile sidebar toggle ---- */
function toggleSidebar() {
    var sidebar = document.querySelector('.sidebar');
    var backdrop = document.getElementById('sidebarBackdrop');
    if (!sidebar) return;

    sidebar.classList.toggle('open');
    if (backdrop) backdrop.classList.toggle('open');
    document.body.classList.toggle('scroll-locked', sidebar.classList.contains('open'));
}

function closeSidebar() {
    var sidebar = document.querySelector('.sidebar');
    var backdrop = document.getElementById('sidebarBackdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
    if (!document.querySelector('.modal-bg.active')) {
        document.body.classList.remove('scroll-locked');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.sidebar a').forEach(function (link) {
        link.addEventListener('click', closeSidebar);
    });
});

window.addEventListener('resize', function () {
    if (window.innerWidth > 1000) closeSidebar();
});

/* ---- Validation helpers ---- */
function showFieldError(field, message) {
    field.classList.add('input-error');
    field.style.borderColor = '#E5484D';

    var wrap = field.closest('.field') || field.parentElement;
    var err = wrap.querySelector('.js-error-msg');

    if (!err) {
        err = document.createElement('div');
        err.className = 'js-error-msg';
        err.style.color = '#B3261E';
        err.style.fontSize = '11.5px';
        err.style.marginTop = '4px';
        wrap.appendChild(err);
    }
    err.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('input-error');
    field.style.borderColor = '';

    var wrap = field.closest('.field') || field.parentElement;
    var err = wrap.querySelector('.js-error-msg');
    if (err) err.remove();
}

function clearFormErrors(scope) {
    scope.querySelectorAll('.js-error-msg').forEach(function (el) { el.remove(); });
    scope.querySelectorAll('.input-error').forEach(function (el) {
        el.classList.remove('input-error');
        el.style.borderColor = '';
    });
}

function isBlank(value) {
    return !value || value.trim().length === 0;
}

function validateCommonFields(form) {
    var valid = true;

    form.querySelectorAll('input[required], select[required]').forEach(function (field) {
        clearFieldError(field);

        if (field.tagName === 'SELECT') {
            if (isBlank(field.value)) {
                showFieldError(field, 'Please select an option.');
                valid = false;
            }
            return;
        }

        if (field.type === 'number') {
            var num = parseFloat(field.value);
            if (isBlank(field.value) || isNaN(num)) {
                showFieldError(field, 'This field is required.');
                valid = false;
            } else if (num <= 0) {
                showFieldError(field, 'Value must be greater than 0.');
                valid = false;
            }
            return;
        }

        if (field.type === 'date') {
            if (isBlank(field.value)) {
                showFieldError(field, 'Please select a date.');
                valid = false;
            }
            return;
        }

        if (isBlank(field.value)) {
            showFieldError(field, 'This field is required.');
            valid = false;
        }
    });

    return valid;
}

/* ---- Field specific rules ---- */
function validateSessionDates(form) {
    var start = form.querySelector('input[name="start_date"]');
    var end = form.querySelector('input[name="end_date"]');
    if (!start || !end || isBlank(start.value) || isBlank(end.value)) return true;

    if (new Date(end.value) < new Date(start.value)) {
        showFieldError(end, 'End date cannot be before start date.');
        return false;
    }
    clearFieldError(end);
    return true;
}

var INPUT_FILTERS = {
    name: function (value) {
        return value.replace(/[^A-Za-z0-9\s.'&-]/g, '');
    },

    contact_person: function (value) {
        return value.replace(/[^A-Za-z\s.'-]/g, '');
    },

    department: function (value) {
        return value.replace(/[^A-Za-z\s.'-]/g, '');
    },

    symbol: function (value) {
        return value.replace(/[^A-Za-z]/g, '');
    },

    code: function (value) {
        return value.replace(/[^A-Za-z0-9\-_]/g, '');
    },

    phone: function (value) {
        return value.replace(/[^0-9]/g, '').slice(0, 10);
    },

    location: function (value) {
        return value.replace(/[^A-Za-z0-9\s,\-\/#]/g, '');
    }
};

function attachInputFilters(form) {
    Object.keys(INPUT_FILTERS).forEach(function (fieldName) {
        var field = form.querySelector('[name="' + fieldName + '"]');
        if (!field) return;

        field.addEventListener('input', function () {
            var cleaned = INPUT_FILTERS[fieldName](field.value);
            if (cleaned !== field.value) {
                field.value = cleaned;
            }
        });
    });
}

function tooManyDashes(value) {
    return (value.match(/-/g) || []).length > 2;
}

var FIELD_RULES = {
    phone: function (value) {
        if (!/^[6-9]\d{9}$/.test(value)) {
            return 'Enter a valid 10-digit mobile number.';
        }
        return null;
    },

    contact_person: function (value) {
        if (!/^[A-Za-z\s.'-]{2,100}$/.test(value)) {
            return 'Only letters allowed (numbers not permitted).';
        }
        if (!/[A-Za-z]/.test(value)) {
            return 'Must contain at least one letter.';
        }
        if (tooManyDashes(value)) {
            return 'Can have at most 2 hyphens.';
        }
        return null;
    },

    code: function (value) {
        if (!/^[A-Za-z0-9\-_]{1,20}$/.test(value)) {
            return 'Only letters, numbers, - and _ allowed (max 20 chars).';
        }
        if (!/[A-Za-z0-9]/.test(value)) {
            return 'Must contain at least one letter or number.';
        }
        if (tooManyDashes(value)) {
            return 'Can have at most 2 hyphens.';
        }
        return null;
    },

    symbol: function (value) {
        if (!/^[A-Za-z]{1,10}$/.test(value)) {
            return 'Only letters allowed (max 10 characters).';
        }
        return null;
    },

    location: function (value) {
        if (value.length < 2) return 'Must be at least 2 characters.';
        if (value.length > 100) return 'Too long (max 100 characters).';
        if (!/[A-Za-z0-9]/.test(value)) return 'Must contain at least one letter or number.';
        if (tooManyDashes(value)) return 'Can have at most 2 hyphens.';
        return null;
    },

    name: function (value) {
        if (!/^[A-Za-z0-9\s.'&-]{2,100}$/.test(value)) {
            return 'Only letters, numbers, spaces and . \' & - are allowed.';
        }
        if (!/[A-Za-z]/.test(value)) {
            return 'Must contain at least one letter.';
        }
        if (tooManyDashes(value)) {
            return 'Can have at most 2 hyphens.';
        }
        return null;
    },

    department: function (value) {
        if (!/^[A-Za-z\s.'-]{2,100}$/.test(value)) {
            return 'Only letters allowed (numbers not permitted).';
        }
        if (!/[A-Za-z]/.test(value)) {
            return 'Must contain at least one letter.';
        }
        if (tooManyDashes(value)) {
            return 'Can have at most 2 hyphens.';
        }
        return null;
    }
};

function validateFieldRules(form) {
    var valid = true;

    Object.keys(FIELD_RULES).forEach(function (fieldName) {
        var field = form.querySelector('[name="' + fieldName + '"]');
        if (!field) return;

        var value = field.value.trim();
        if (value === '') return;

        var error = FIELD_RULES[fieldName](value);
        if (error) {
            showFieldError(field, error);
            valid = false;
        } else {
            clearFieldError(field);
        }
    });

    return valid;
}

function getSuccessMessage(action) {
    if (action.indexOf('/admin/permissions') !== -1) {
        return 'Permissions updated successfully!';
    }
    if (action.indexOf('/master/product-category') !== -1) {
        return 'Product Category saved successfully!';
    }
    if (action.indexOf('/master/product-master') !== -1) {
        return 'Product Master saved successfully!';
    }
    if (action.indexOf('/master/product') !== -1) {
        return 'Product saved successfully!';
    }
    if (action.indexOf('/master/department') !== -1) {
        return 'Department saved successfully!';
    }
    if (action.indexOf('/master/factory') !== -1) {
        return 'Factory saved successfully!';
    }
    if (action.indexOf('/master/session') !== -1) {
        return 'Session saved successfully!';
    }
    if (action.indexOf('/master/store') !== -1) {
        return 'Store saved successfully!';
    }
    if (action.indexOf('/master/supplier') !== -1) {
        return 'Supplier saved successfully!';
    }
    if (action.indexOf('/master/uom') !== -1) {
        return 'UOM saved successfully!';
    }
    return 'Saved successfully!';
}

/* ---- Topbar search ---- */
function initTopbarSearch() {
    var input = document.querySelector('.topbar-search .search-input');
    var table = document.querySelector('.table-wrap table tbody');
    if (!input || !table) return;

    var ROW_TRANSITION_MS = 160;

    var applyFilter = debounce(function () {
        var q = input.value.trim().toLowerCase();

        // Read pass first (avoid layout thrashing from interleaved reads/writes)
        var rows = Array.prototype.map.call(table.querySelectorAll('tr'), function (row) {
            var text = row.textContent.toLowerCase();
            var matches = (q === '' || text.indexOf(q) !== -1);
            return { row: row, matches: matches };
        });

        // Write pass
        rows.forEach(function (item) {
            var row = item.row;
            if (item.matches) {
                if (row.style.display === 'none') row.style.display = '';
                // allow display to apply before removing the class so the fade-in plays
                requestAnimationFrame(function () {
                    row.classList.remove('row-filtered-out');
                });
            } else {
                if (!row.classList.contains('row-filtered-out')) {
                    row.classList.add('row-filtered-out');
                    setTimeout(function () {
                        if (row.classList.contains('row-filtered-out')) {
                            row.style.display = 'none';
                        }
                    }, ROW_TRANSITION_MS);
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }, 180);

    input.addEventListener('input', applyFilter);
}

document.addEventListener('DOMContentLoaded', initTopbarSearch);

/* ---- Form validation + toasts ---- */
document.addEventListener('DOMContentLoaded', function () {
    var pending = sessionStorage.getItem('pendingToast');
    if (pending) {
        sessionStorage.removeItem('pendingToast');
        showToast(pending);
    }

    if (sessionStorage.getItem('justLoggedIn') === '1') {
        sessionStorage.removeItem('justLoggedIn');
        if (window.location.pathname !== '/login') {
            showToast('Login successful!');
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(function (form) {
        var action = form.getAttribute('action') || '';

        if (action.indexOf('/delete') !== -1) {
            form.addEventListener('submit', function (e) {
                if (!confirm('Delete this record?')) {
                    e.preventDefault();
                    return;
                }
                sessionStorage.setItem('pendingToast', 'Record deleted successfully!');

                var delBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (delBtn && !delBtn.disabled) {
                    delBtn.classList.add('btn-loading');
                    delBtn.disabled = true;
                }
            });
            return;
        }

        var isLoginForm = action.indexOf('/login') !== -1;

        if (!isLoginForm) {
            attachInputFilters(form);
        }

        form.addEventListener('submit', function (e) {
            var ok = validateCommonFields(form);

            if (!isLoginForm) {
                ok = validateFieldRules(form) && ok;
            }

            if (action.indexOf('/master/session') !== -1) {
                ok = validateSessionDates(form) && ok;
            }

            if (!ok) {
                e.preventDefault();
                var firstError = form.querySelector('.input-error');
                if (firstError) firstError.focus();
                return;
            }

            if (isLoginForm) {
                sessionStorage.setItem('justLoggedIn', '1');
            } else {
                sessionStorage.setItem('pendingToast', getSuccessMessage(action));
            }

            var submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.classList.add('btn-loading');
                submitBtn.disabled = true;
            }
        });

        form.querySelectorAll('input, select').forEach(function (field) {
            field.addEventListener('input', function () { clearFieldError(field); });
            field.addEventListener('change', function () { clearFieldError(field); });
        });
    });
});