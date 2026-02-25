// SPDX-License-Identifier: FSL-1.1-MIT
"use strict";

(function () {
    function toggleChainsField() {
        var scopeSelect = document.getElementById("id_scope");
        var chainsField = document.querySelector(".field-chains");
        if (!scopeSelect || !chainsField) return;
        chainsField.style.display = scopeSelect.value === "GLOBAL" ? "none" : "";
    }

    document.addEventListener("DOMContentLoaded", function () {
        toggleChainsField();
        var scopeSelect = document.getElementById("id_scope");
        if (scopeSelect) {
            scopeSelect.addEventListener("change", toggleChainsField);
        }
    });
})();
