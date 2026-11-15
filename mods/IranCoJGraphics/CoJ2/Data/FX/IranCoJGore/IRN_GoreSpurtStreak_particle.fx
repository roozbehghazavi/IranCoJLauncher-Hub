ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.4)
	}

	GravityMul()
	{
		randf(0, 1, 1.1)
	}

	Drag()
	{
		randf(0, 0.3, 0.5)
	}

	Color()
	{
		keyv4(0, 0.75, 0.75, 0.75, 1)
		keyv4(0.6, 0.75, 0.75, 0.75, 0.9)
		keyv4(1.4, 0.75, 0.75, 0.75, 0.6)
	}

	Size()
	{
		randf(0, 8, 12)
	}

	Align("always")

	AspectRatio()
	{
		randf(0, 0.2, 0.3)
	}

	Material("IRN_BloodLine_particleBLEND.mat", "IRN_BloodLine_particleBLEND.mat")

	TexMultiRect(4, 1, 4)
	TexPlayMode("random_once", 1)
}
