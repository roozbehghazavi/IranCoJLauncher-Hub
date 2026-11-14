EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 4)
	}

	GenType("continous")

	ParticleRate()
	{
		keyf(0, 7)
		keyf(1.2, 4)
		keyf(1.5, 0)
	}

	StartVelocity()
	{
		keyf(0, 8)
	}

	StartVelocityRand()
	{
		keyv(0, 4, 4, 4)
	}

	Direction()
	{
		keyv(0, 0, 0, 1)
	}

	GenArea("point")
}
