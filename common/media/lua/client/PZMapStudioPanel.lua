-- Minimal in-game panel for the Java bridge.
PZMapStudioPanel = ISPanel:derive("PZMapStudioPanel")

function PZMapStudioPanel:new(x, y, w, h)
    local o = ISPanel:new(x, y, w, h)
    setmetatable(o, self)
    self.__index = self
    o.backgroundColor = {r=0.04, g=0.06, b=0.05, a=0.92}
    o.borderColor = {r=0.35, g=0.55, b=0.35, a=1}
    o.lines = {}
    return o
end

function PZMapStudioPanel:createChildren()
    ISPanel.createChildren(self)
    self.pathEntry = ISTextEntryBox:new(getZomboidDirectory() .. "/PZMapStudio/scene.json",
        12, self.height - 108, self.width - 24, 24)
    self.pathEntry:initialise()
    self.pathEntry:instantiate()
    self:addChild(self.pathEntry)

    self.commandEntry = ISTextEntryBox:new(
        '{"op":"paint","layer":"roads","x":0,"y":0,"w":20,"h":4,"tile":"asphalt"}',
        12, self.height - 78, self.width - 24, 24)
    self.commandEntry:initialise()
    self.commandEntry:instantiate()
    self:addChild(self.commandEntry)

    self.cellX = ISTextEntryBox:new("0", 12, self.height - 48, 45, 24)
    self.cellX:initialise(); self.cellX:instantiate(); self:addChild(self.cellX)
    self.cellY = ISTextEntryBox:new("0", 62, self.height - 48, 45, 24)
    self.cellY:initialise(); self.cellY:instantiate(); self:addChild(self.cellY)

    local run = ISButton:new(115, self.height - 48, 96, 26, "Execute", self, PZMapStudioPanel.execute)
    run:initialise(); run:instantiate(); self:addChild(run)

    local new = ISButton:new(216, self.height - 48, 96, 26, "New scene", self, PZMapStudioPanel.newScene)
    new:initialise(); new:instantiate(); self:addChild(new)

    local export = ISButton:new(316, self.height - 48, 120, 26, "Stage cell", self, PZMapStudioPanel.exportCell)
    export:initialise(); export:instantiate(); self:addChild(export)

    local close = ISButton:new(self.width - 90, self.height - 48, 80, 26, "Close", self, PZMapStudioPanel.close)
    close:initialise(); close:instantiate(); self:addChild(close)
end

function PZMapStudioPanel:execute()
    local api = PZMapStudioAPI and PZMapStudioAPI.getInstance()
    if not api then print("[PZMapStudio] Java API missing"); return end
    local ok, result = pcall(function()
        return api:command(self.pathEntry:getText(), self.commandEntry:getText())
    end)
    print("[PZMapStudio] " .. tostring(result))
end

function PZMapStudioPanel:newScene()
    local api = PZMapStudioAPI and PZMapStudioAPI.getInstance()
    if not api then return end
    local ok, result = pcall(function()
        return api:newScene(self.pathEntry:getText(), 512, 512)
    end)
    print("[PZMapStudio] " .. tostring(result))
end

function PZMapStudioPanel:exportCell()
    local api = PZMapStudioAPI and PZMapStudioAPI.getInstance()
    if not api then print("[PZMapStudio] Java API missing"); return end
    local out = getZomboidDirectory() .. "/PZMapStudio/export"
    local cx = tonumber(self.cellX:getText()) or 0
    local cy = tonumber(self.cellY:getText()) or 0
    local ok, result = pcall(function()
        return api:exportCell(self.pathEntry:getText(), cx, cy, out)
    end)
    print("[PZMapStudio] " .. tostring(result))
end

function PZMapStudioPanel:close()
    self:setVisible(false)
    self:removeFromUIManager()
end

function PZMapStudioPanel:setLines(lines)
    self.lines = lines or {}
end

function PZMapStudioPanel:render()
    ISPanel.render(self)
    self:drawText("PZMapStudio", 12, 10, 0.9, 1, 0.85, 1, UIFont.Medium)
    local y = 40
    for _, line in ipairs(self.lines) do
        self:drawText(tostring(line), 12, y, 0.85, 0.9, 0.85, 1, UIFont.Small)
        y = y + 18
    end
end

local function openPanel()
    if not PZMapStudioPanel.instance then
        PZMapStudioPanel.instance = PZMapStudioPanel:new(
            getCore():getScreenWidth() / 2 - 300,
            getCore():getScreenHeight() / 2 - 180,
            600, 360)
        PZMapStudioPanel.instance:initialise()
        PZMapStudioPanel.instance:addToUIManager()
    end
    local lines = {}
    if PZMapStudioAPI then
        local api = PZMapStudioAPI.getInstance()
        table.insert(lines, api:status())
        table.insert(lines, api:help())
    else
        table.insert(lines, "Java API not loaded.")
        table.insert(lines, "Approve PZMapStudio.jar in ZombieBuddy if prompted.")
    end
    PZMapStudioPanel.instance:setLines(lines)
    PZMapStudioPanel.instance:setVisible(true)
end

local function togglePanel()
    if PZMapStudioPanel.instance and PZMapStudioPanel.instance:isVisible() then
        PZMapStudioPanel.instance:close()
    else
        openPanel()
    end
end

Events.OnKeyPressed.Add(function(key)
    if key == Keyboard.KEY_F10 then
        togglePanel()
    end
end)
