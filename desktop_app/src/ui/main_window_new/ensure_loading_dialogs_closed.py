def ensure_loading_dialogs_closed(self):
        """
        Safety method to ensure all loading dialogs are closed.
        This is a fail-safe to prevent hanging dialogs, especially when there are no images
        or when operations fail with exceptions.
        
        This method is EXTREMELY aggressive in finding and closing dialogs to prevent UI hangs.
        It will find and close ALL dialogs related to loading, refreshing, or product images.
        """
        try:
            print("EMERGENCY: Forcing closure of all loading dialogs")
            
            # First, ensure no events are pending that might interfere
            QApplication.processEvents()
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()  # Double process to catch everything
            
            # First, check our tracked dialog list for direct cleanup
            if hasattr(self, 'active_loading_dialogs') and self.active_loading_dialogs:
                print(f"Found {len(self.active_loading_dialogs)} tracked loading dialogs to close")
                for dialog in self.active_loading_dialogs[:]:  # Use a copy of the list to safely modify during iteration
                    try:
                        if dialog and not dialog.isHidden():  # Check if dialog still exists and is visible
                            print(f"Closing tracked dialog: {dialog.windowTitle() if hasattr(dialog, 'windowTitle') else 'unnamed'}")
                            # Try all possible ways to close this tracked dialog
                            for close_method in ['reject', 'done', 'close', 'hide']:
                                try:
                                    if hasattr(dialog, close_method) and callable(getattr(dialog, close_method)):
                                        if close_method == 'done':
                                            getattr(dialog, close_method)(0)  # done(0) for rejection
                                        else:
                                            getattr(dialog, close_method)()
                                except Exception:
                                    pass
                            
                            try:
                                dialog.deleteLater()  # Schedule deletion
                            except Exception:
                                pass
                                
                            QApplication.processEvents()  # Process each close immediately
                    except Exception as dialog_err:
                        print(f"Error closing tracked dialog: {str(dialog_err)}")
                    
                    # Remove from tracking list regardless of success
                    try:
                        self.active_loading_dialogs.remove(dialog)
                    except Exception:
                        pass
                
                # Clear the list completely after attempting to close all dialogs
                self.active_loading_dialogs = []
            
            # Multiple attempts loop to ensure we catch everything
            # Sometimes one pass isn't enough due to event loop timing
            for attempt in range(4):  # Increased to 4 attempts for more reliability
                # AGGRESSIVELY find and close any QMessageBox or QDialog with loading-related text
                closed_count = 0
                for widget in QApplication.topLevelWidgets():
                    try:
                        # Check for QMessageBox dialogs
                        if isinstance(widget, QMessageBox):
                            # Try to get title and text with robust error handling
                            title = ""
                            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                                title = widget.windowTitle()
                                
                            text = ""
                            if hasattr(widget, 'text') and callable(widget.text):
                                text = widget.text()
                            
                            # ULTRA aggressive checks - even more conditions to match ANY loading dialog
                            # Include P7111001 as a specific match since that's giving us trouble
                            if ('Loading' in title or 'Refreshing' in title or 'Processing' in title or
                                'Loading' in text or 'Refreshing' in text or 'Processing' in text or
                                'product images' in text.lower() or 'image' in text.lower() or
                                'barcode' in text.lower() or 'P7111001' in text or
                                'THM1101' in text or 'Uploading' in text):
                                print(f"FORCE CLOSING dialog: {title} - {text}")
                                
                                # Try all possible ways to close this widget
                                for close_method in ['reject', 'done', 'close', 'hide']:
                                    try:
                                        if hasattr(widget, close_method) and callable(getattr(widget, close_method)):
                                            if close_method == 'done':
                                                getattr(widget, close_method)(0)  # done(0) for rejection
                                            else:
                                                getattr(widget, close_method)()
                                    except Exception:
                                        pass
                                
                                try:
                                    widget.deleteLater()  # Always try to schedule deletion
                                except Exception:
                                    pass
                                    
                                closed_count += 1
                                QApplication.processEvents()  # Process each close immediately
                        
                        # Also check for QDialog instances with loading-related titles
                        elif isinstance(widget, QDialog):
                            title = ""
                            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                                title = widget.windowTitle()
                                
                            # Check for ANY dialog that might be related to loading or images
                            if ('Loading' in title or 'Refreshing' in title or 'Images' in title or
                                'Processing' in title or 'Upload' in title or 'Product' in title):
                                print(f"FORCE CLOSING QDialog: {title}")
                                
                                # Try all possible ways to close this widget
                                for close_method in ['reject', 'done', 'close', 'hide']:
                                    try:
                                        if hasattr(widget, close_method) and callable(getattr(widget, close_method)):
                                            if close_method == 'done':
                                                getattr(widget, close_method)(0)  # done(0) for rejection
                                            else:
                                                getattr(widget, close_method)()
                                    except Exception:
                                        pass
                                
                                try:
                                    widget.deleteLater()  # Always try to schedule deletion
                                except Exception:
                                    pass
                                    
                                closed_count += 1
                                QApplication.processEvents()  # Process each close immediately
                    except Exception as widget_err:
                        print(f"Error processing widget during cleanup: {str(widget_err)}")
                
                # If nothing was closed in this attempt, no need for more attempts
                if closed_count == 0 and attempt > 0:
                    break
                    
                # Process events between attempts
                QApplication.processEvents()
            
            # Aggressively clean the images grid - find ANYTHING with loading text
            if hasattr(self, 'images_grid') and self.images_grid:
                # Safety check for C++ object deleted situations
                grid_is_valid = True
                try:
                    # Check if the layout is still valid by trying to access count()
                    grid_count = self.images_grid.count()
                except RuntimeError as e:
                    print(f"Warning: images_grid has been deleted or is invalid: {str(e)}")
                    grid_is_valid = False
                    
                if grid_is_valid:
                    try:
                        # First pass: remove any labels with loading text
                        for i in range(self.images_grid.count()):
                            try:
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widget = item.widget()
                                    
                                    # Check for loading indicators in QLabels
                                    if isinstance(widget, QLabel):
                                        try:
                                            label_text = widget.text().lower()
                                            if ('loading' in label_text or 'refreshing' in label_text or 
                                                'product image' in label_text):
                                                print(f"Removing grid widget: {widget.text()}")
                                                widget.setParent(None)
                                                widget.deleteLater()
                                                QApplication.processEvents()
                                        except Exception:
                                            # If we can't get text, try to remove it anyway
                                            widget.setParent(None)
                                            widget.deleteLater()
                                            QApplication.processEvents()
                            except Exception as item_err:
                                print(f"Error cleaning grid item: {str(item_err)}")
                    except RuntimeError:
                        # Layout became invalid during the first pass
                        print("Grid layout became invalid during cleanup, skipping remaining operations")
                        grid_is_valid = False
                                
                    # Second pass: complete clearance if needed - prepare list first
                    if grid_is_valid:
                        try:
                            # Get all widgets to be removed
                            widgets_to_remove = []
                            for i in range(self.images_grid.count()):
                                item = self.images_grid.itemAt(i)
                                if item and item.widget():
                                    widgets_to_remove.append(item.widget())
                            
                            # Now actually remove them
                            for widget in widgets_to_remove:
                                try:
                                    self.images_grid.removeWidget(widget)
                                    widget.setParent(None)
                                    widget.deleteLater()
                                    QApplication.processEvents()
                                except Exception:
                                    # If we can't remove it one way, try other ways
                                    try:
                                        widget.hide()
                                    except Exception:
                                        pass
                        except Exception as grid_err:
                            print(f"Error in complete grid cleaning: {str(grid_err)}")
            
            # Update image preview to refresh the UI state
            try:
                self.update_image_preview()
            except Exception as update_err:
                print(f"Error updating image preview after cleanup: {str(update_err)}")
            
            # Force process all events to update UI - multiple passes for reliability
            QApplication.processEvents()
            QApplication.sendPostedEvents(None, 0)
            QApplication.processEvents()
            
        except Exception as e:
            print(f"Error in ensure_loading_dialogs_closed: {str(e)}")
