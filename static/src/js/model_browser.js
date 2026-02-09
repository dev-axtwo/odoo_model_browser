/** @odoo-module **/

import { Component, useState, useRef, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { rpc } from "@web/core/network/rpc";

/**
 * Model Browser - Quick access to all Odoo models
 * Similar to "All Functions" in 1C
 */
export class ModelBrowser extends Component {
    static template = "model_browser.ModelBrowser";
    static props = {};

    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            isOpen: false,
            searchTerm: "",
            models: [],
            loading: false,
            selectedIndex: 0,
        });
        
        this.searchInputRef = useRef("searchInput");
        this.searchTimeout = null;
        
        // Keyboard shortcut: Alt+M to open
        useHotkey("alt+m", () => this.toggleBrowser());
        
        onWillUnmount(() => {
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
        });
    }

    toggleBrowser() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            this.state.searchTerm = "";
            this.state.selectedIndex = 0;
            this.loadModels();
            // Focus search input after render
            setTimeout(() => {
                const input = this.searchInputRef.el;
                if (input) {
                    input.focus();
                }
            }, 100);
        }
    }

    closeBrowser() {
        this.state.isOpen = false;
    }

    async loadModels() {
        this.state.loading = true;
        try {
            const models = await rpc("/model_browser/search", {
                search_term: this.state.searchTerm,
                limit: 50,
            });
            this.state.models = models;
            this.state.selectedIndex = 0;
        } catch (error) {
            console.error("Failed to load models:", error);
            this.notification.add(_t("Failed to load models"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    onSearchInput(ev) {
        this.state.searchTerm = ev.target.value;
        
        // Debounce search
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        this.searchTimeout = setTimeout(() => {
            this.loadModels();
        }, 200);
    }

    onSearchKeydown(ev) {
        const models = this.state.models;
        
        switch (ev.key) {
            case "ArrowDown":
                ev.preventDefault();
                if (this.state.selectedIndex < models.length - 1) {
                    this.state.selectedIndex++;
                    this.scrollToSelected();
                }
                break;
            case "ArrowUp":
                ev.preventDefault();
                if (this.state.selectedIndex > 0) {
                    this.state.selectedIndex--;
                    this.scrollToSelected();
                }
                break;
            case "Enter":
                ev.preventDefault();
                if (models[this.state.selectedIndex]) {
                    this.openModel(models[this.state.selectedIndex]);
                }
                break;
            case "Escape":
                ev.preventDefault();
                this.closeBrowser();
                break;
        }
    }

    scrollToSelected() {
        setTimeout(() => {
            const selected = document.querySelector(".model-browser-item.selected");
            if (selected) {
                selected.scrollIntoView({ block: "nearest", behavior: "smooth" });
            }
        }, 10);
    }

    async openModel(model) {
        this.closeBrowser();
        try {
            const action = await rpc("/model_browser/open", {
                model_name: model.model,
            });
            if (action) {
                await this.action.doAction(action);
            } else {
                this.notification.add(
                    _t("Cannot open model: %s", model.model),
                    { type: "warning" }
                );
            }
        } catch (error) {
            console.error("Failed to open model:", error);
            this.notification.add(_t("Failed to open model"), { type: "danger" });
        }
    }

    formatCount(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + "M";
        }
        if (count >= 1000) {
            return (count / 1000).toFixed(1) + "K";
        }
        return count.toString();
    }
}

// Register in systray
registry.category("systray").add("model_browser", {
    Component: ModelBrowser,
}, { sequence: 1 });
